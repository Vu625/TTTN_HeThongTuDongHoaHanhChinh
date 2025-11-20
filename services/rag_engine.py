#Chứa các hàm Numpy để Vector Search, Similarity Search (Custom RAG).
import os
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
from pathlib import Path
from collections import Counter
import math
from scipy.sparse import csr_matrix, save_npz, load_npz
from scipy.sparse.linalg import norm as sparse_norm
import pickle
BASE_DIR = Path(__file__).resolve().parent.parent   # nhảy ra khỏi services/
LAW_DIR = BASE_DIR / "data/db/law_texts"
Path_Vecto = Path("data/db/database_vecto")
def load_law_texts():
    texts = []
    for file in LAW_DIR.glob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            texts.append((file.name, f.read()))
    return texts

def build_vector_store():
    texts = load_law_texts()
    docs = [t[1] for t in texts]
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(docs)
    return texts, vectorizer, vectors

def retrieve_relevant_text(query, vectorizer, vectors, texts, top_k=1):
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, vectors).flatten()
    top_indices = similarities.argsort()[-top_k:][::-1]
    results = [(texts[i][0], texts[i][1], similarities[i]) for i in top_indices]
    return results

def generate_answer(query):
    texts, vectorizer, vectors = build_vector_store()
    results = retrieve_relevant_text(query, vectorizer, vectors, texts)
    if not results:
        return "Xin lỗi, tôi không tìm thấy quy định phù hợp."
    filename, content, score = results[0]
    return f"📘 Theo **{filename}**:\n\n{content.strip()}\n\n(Độ liên quan: {score:.2f})"

def read_txt(filename):
    file_path = (LAW_DIR / filename).resolve()
    print("🔍 Đang load file:", file_path)
    if not file_path.exists():
        print(f"⚠️ File {file_path} không tồn tại!")
        return ""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
def split_into_chunks(text):
    chunks = []

    # 1) Tách tên Nghị định (giả sử dòng đầu hoặc có "Nghị định")
    match_nghidinh = re.search(r'(Nghị định.*?)(\n|$)', text, re.IGNORECASE)
    nghidinh_title = ""
    if match_nghidinh:
        nghidinh_title = match_nghidinh.group(1).strip()
        # Loại bỏ phần tiêu đề ra khỏi text
        text = text[match_nghidinh.end():].strip()

    # 2) Tách theo Chương
    chuong_pattern = r'(Chương\s+\w+.*?)(?=\nChương|\Z)'
    chuong_list = re.findall(chuong_pattern, text, flags=re.DOTALL)

    for chuong_block in chuong_list:
        # Lấy tên Chương (dòng đầu)
        chuong_title = chuong_block.split("\n")[0].strip()

        # Nội dung còn lại của Chương
        chuong_content = chuong_block[len(chuong_title):].strip()

        # 3) Tách theo Điều
        dieu_pattern = r'(Điều\s+\d+\.)'
        dieu_splits = re.split(dieu_pattern, chuong_content)

        for i in range(1, len(dieu_splits), 2):
            dieu_number = dieu_splits[i].strip()
            dieu_title = re.split('\n', dieu_splits[i+1])[0]
            dieu_content = dieu_splits[i+1]

            # 4) Tách theo Khoản
            khoan_pattern = r'(?m)^(\d+\.)'
            khoan_splits = re.split(khoan_pattern, dieu_content)

            if len(khoan_splits) == 1:
                # Nếu điều không có khoản → chunk cả điều
                # chunk = (
                #     f"{nghidinh_title}\n"
                #     f"{chuong_title}\n"
                #     f"{dieu_title}\n"
                #     f"{khoan_splits[0].strip()}"
                # )
                # chunks.append(chunk)
                chunks.append({
                    'content': khoan_splits[0].strip(),
                    'metadata': {
                        'Decree': nghidinh_title,
                        'Chapter': chuong_title,
                        'article_number': dieu_number,
                        'article': dieu_title,
                        'Clause': " ",
                    }
                })
            else:
                # Nếu có khoản → mỗi khoản 1 chunk
                for k in range(1, len(khoan_splits), 2):
                    khoan_num = khoan_splits[k].replace(".", "")
                    khoan_text = khoan_splits[k+1].strip()

                    # chunk = (
                    #     f"{nghidinh_title}\n"
                    #     f"{chuong_title}\n"
                    #     f"{dieu_title} Khoản {khoan_num}\n"
                    #     f"{khoan_text}"
                    # )
                    # chunks.append(chunk)
                    chunks.append({
                        'content': khoan_text,
                        'metadata': {
                            'Decree': nghidinh_title,
                            'Chapter': chuong_title,
                            'article_number': dieu_number,
                            'article': dieu_title,
                            'Clause': khoan_num,
                        }
                    })

    return chunks

class CustomTfidfVectorizer:
    def __init__(self, stop_words=None):
        self.vocabulary = {}
        self.idf = {}
        self.stop_words = set(stop_words) if stop_words else set()

    def _tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def fit(self, raw_documents):
        term_document_frequency = Counter()
        document_count = len(raw_documents)

        for doc in raw_documents:
            tokens = self._tokenize(doc)
            unique_tokens = set(tokens)
            term_document_frequency.update(unique_tokens)

        # self.vocabulary = {term: idx for idx, term in enumerate(term_document_frequency.keys())
        #                    if term not in self.stop_words}
        valid_terms = [term for term in term_document_frequency.keys()
                       if term not in self.stop_words]

        # Chỉ số phải được gán tuần tự dựa trên danh sách đã lọc
        self.vocabulary = {term: idx for idx, term in enumerate(valid_terms)}

        self.idf = {
            term: math.log((document_count + 1) / (df + 1)) + 1
            for term, df in term_document_frequency.items()
            if term in self.vocabulary
        }
        return self

    def transform(self, raw_documents):
        num_docs = len(raw_documents)
        num_features = len(self.vocabulary)
        data, row_ind, col_ind = [], [], []

        for doc_index, doc in enumerate(raw_documents):
            tokens = self._tokenize(doc)
            term_counts = Counter(tokens)
            total_tokens = len(tokens)

            for term, count in term_counts.items():
                if term in self.vocabulary:
                    term_index = self.vocabulary[term]
                    tf = count / total_tokens
                    idf = self.idf.get(term, 0)
                    tfidf_score = tf * idf
                    data.append(tfidf_score)
                    row_ind.append(doc_index)
                    col_ind.append(term_index)

        tfidf_matrix = csr_matrix((data, (row_ind, col_ind)), shape=(num_docs, num_features))
        norms = np.sqrt(tfidf_matrix.power(2).sum(axis=1))
        norms[norms == 0] = 1
        tfidf_matrix = tfidf_matrix.multiply(1 / norms)
        return tfidf_matrix

# ===============================
# Save/Load Index
# ===============================
# def save_index(vectorizer, tfidf_matrix, chunks, index_prefix):
#     with open(Path_Vecto / f"{index_prefix}_vectorizer.pkl", "wb") as f:
#         pickle.dump(vectorizer, f)
#     save_npz(Path_Vecto / f"{index_prefix}_matrix.npz", tfidf_matrix)
#     with open(Path_Vecto / f"{index_prefix}_chunks.pkl", 'wb') as f:
#         pickle.dump(chunks, f)
#     print("✅ Đã lưu trữ Index thành công!")

from pathlib import Path
import pickle
from scipy.sparse import save_npz

# BASE_DIR: thư mục gốc của project
BASE_DIR = Path(__file__).resolve().parent.parent

# VECTOR_DIR: thư mục lưu vector
VECTOR_DIR = BASE_DIR / "data/db/database_vecto"


def save_index(vectorizer, tfidf_matrix, chunks, index_prefix):

    # 🔥 Tạo folder nếu chưa có
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)

    # 🔥 In ra để debug
    print("📂 Lưu index vào:", VECTOR_DIR.resolve())

    # --- Lưu vectorizer ---
    vec_path = VECTOR_DIR / f"{index_prefix}_vectorizer.pkl"
    with open(vec_path, "wb") as f:
        pickle.dump(vectorizer, f)

    # --- Lưu matrix ---
    mat_path = VECTOR_DIR / f"{index_prefix}_tfidf_matrix.npz"
    save_npz(mat_path, tfidf_matrix)

    # --- Lưu chunks ---
    chunks_path = VECTOR_DIR / f"{index_prefix}_chunks.pkl"
    with open(chunks_path, "wb") as f:
        pickle.dump(chunks, f)

    print("✅ Lưu thành công:", index_prefix)

# def load_index(index_prefix):
#     with open(Path_Vecto / f"{index_prefix}_vectorizer.pkl", 'rb') as f:
#         vectorizer = pickle.load(f)
#     tfidf_matrix = load_npz(Path_Vecto / f"{index_prefix}_matrix.npz")
#     with open(Path_Vecto / f"{index_prefix}_chunks.pkl", 'rb') as f:
#         chunks = pickle.load(f)
#     return vectorizer, tfidf_matrix, chunks

def load_index(index_prefix):

    # 🔍 Debug: xem đường dẫn thực tế
    print("📂 Đang load index từ:", VECTOR_DIR.resolve())

    vec_path = VECTOR_DIR / f"{index_prefix}_vectorizer.pkl"
    mat_path = VECTOR_DIR / f"{index_prefix}_tfidf_matrix.npz"
    chunks_path = VECTOR_DIR / f"{index_prefix}_chunks.pkl"

    # --- Kiểm tra file tồn tại ---
    if not vec_path.exists():
        raise FileNotFoundError(f"❌ Không tìm thấy: {vec_path}")
    if not mat_path.exists():
        raise FileNotFoundError(f"❌ Không tìm thấy: {mat_path}")
    if not chunks_path.exists():
        raise FileNotFoundError(f"❌ Không tìm thấy: {chunks_path}")

    # --- Load vectorizer ---
    with open(vec_path, "rb") as f:
        vectorizer = pickle.load(f)

    # --- Load matrix ---
    tfidf_matrix = load_npz(mat_path)

    # --- Load chunks ---
    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)

    print(f"✅ Load thành công: {index_prefix}")
    return vectorizer, tfidf_matrix, chunks
def vector_search_boosted(query, vectorizer, tfidf_matrix, chunks, k=5, boost_factor=1.5):
    query_vector = vectorizer.transform([query])
    if query_vector.shape[1] == 0:
        return []
    q_norm = sparse_norm(query_vector)
    if q_norm == 0:
        return []
    normalized_query = query_vector.multiply(1 / q_norm)
    similarity_scores = normalized_query.dot(tfidf_matrix.T).toarray()[0]

    primary_keywords = ["nguyên tắc", "phạm vi", "hệ thống", "thẩm quyền", "hiệu lực", "giải thích"]
    boosted_scores = np.copy(similarity_scores)
    query_lower = query.lower()
    is_query_focused_on_primary_keyword = any(kw in query_lower for kw in primary_keywords)

    if is_query_focused_on_primary_keyword:
        for idx, chunk in enumerate(chunks):
            first_line_content = chunk['content'].split('\n')[0].lower()
            should_boost = any(kw in first_line_content and kw in query_lower for kw in primary_keywords)
            if should_boost:
                boosted_scores[idx] = similarity_scores[idx] * boost_factor

    top_indices = np.argsort(boosted_scores)[::-1][:k]
    results = []
    for idx in top_indices:
        if boosted_scores[idx] > 0:
            results.append({
                'score_boosted': boosted_scores[idx],
                'score_original': similarity_scores[idx],
                'content': chunks[idx]['content'],
                'metadata': chunks[idx]['metadata']
            })
    return results

def prepare(file_name):
    word_stop = ["là","thì","của"]
    text = read_txt(file_name)
    chunks = split_into_chunks(text)
    raw_texts = [chunk['content'] for chunk in chunks]
    vectorizer = CustomTfidfVectorizer(stop_words=word_stop).fit(raw_texts)
    tfidf_matrix = vectorizer.transform(raw_texts)
    print(f"✅ Ma trận TF-IDF đã tạo: **{tfidf_matrix.shape}**")
    name = file_name.split('.')[0]
    save_index(vectorizer, tfidf_matrix, chunks, name)

prepare("NghiDinhThue.txt")
