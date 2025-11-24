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
import glob
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

    primary_keywords = [# --- Nhóm pháp lý – cấu trúc văn bản ---
        "Nghị định", "Luật Đất đai", "thi hành",
        "điều khoản", "khoản", "điểm", "chương",
        "phạm vi điều chỉnh", "đối tượng áp dụng",
        "quy định chi tiết", "hướng dẫn thi hành",
        "căn cứ", "hiệu lực", "trách nhiệm thi hành",

        # --- Nhóm loại đất ---
        "đất đai", "đất nông nghiệp", "đất phi nông nghiệp",
        "đất trồng lúa", "đất trồng cây hàng năm",
        "đất trồng cây lâu năm", "đất rừng",
        "đất rừng đặc dụng", "đất rừng phòng hộ",
        "đất rừng sản xuất", "đất nuôi trồng thủy sản",
        "đất chăn nuôi", "đất làm muối", "đất nông nghiệp khác",

        "đất ở", "đất ở tại nông thôn", "đất ở tại đô thị",
        "đất xây dựng trụ sở", "đất quốc phòng", "đất an ninh",
        "đất công cộng", "đất giao thông", "đất thủy lợi",
        "đất công trình công cộng", "đất khu công nghiệp",
        "đất thương mại dịch vụ", "đất sản xuất kinh doanh",
        "đất cơ sở sản xuất phi nông nghiệp",

        # --- Nhóm đối tượng sử dụng/quản lý ---
        "người sử dụng đất", "cơ quan nhà nước",
        "Bộ Tài nguyên và Môi trường",
        "chủ sở hữu toàn dân về đất đai",
        "cá nhân trực tiếp sản xuất nông nghiệp",
        "cán bộ", "công chức", "viên chức",
        "người hưởng lương hưu", "người nghỉ mất sức",
        "hợp đồng lao động",

        # --- Nhóm hành vi/hoạt động đất đai ---
        "giao đất", "thuê đất", "công nhận quyền sử dụng đất",
        "chuyển quyền sử dụng đất", "chuyển mục đích sử dụng đất",
        "quy hoạch", "kế hoạch sử dụng đất",
        "thẩm quyền", "thu hồi đất",
        "bồi thường", "hỗ trợ", "tái định cư",

        # --- Nhóm công trình ---
        "trụ sở cơ quan", "công trình sự nghiệp",
        "cơ sở văn hóa", "cơ sở y tế", "cơ sở giáo dục",
        "cơ sở đào tạo", "cơ sở thể dục thể thao",
        "cơ sở khoa học công nghệ", "cơ sở môi trường",
        "cơ sở khí tượng thủy văn", "cơ sở ngoại giao",

        # --- Thuật ngữ trọng yếu đất đai ---
        "quyền sử dụng đất", "giá đất", "định giá đất",
        "sổ đỏ", "giấy chứng nhận", "giấy chứng nhận quyền sử dụng đất",
        "hồ sơ địa chính", "bản đồ địa chính",
        "đăng ký đất đai", "hệ thống thông tin đất đai",
        "cơ sở dữ liệu đất đai",
        "hành lang an toàn", "khu vực bảo vệ",
        "khu vực cấm", "khu vực hạn chế"]
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
    word_stop = ["a", "à", "á", "ạ", "ả", "ã",
        "ào", "ạ", "ai", "alô", "ào", "ạ",
        "anh", "anh ấy", "ba", "bác", "bạn", "bằng",
        "bị", "bình", "bộ", "bỗng", "bởi", "bởi vì", "bớ",
        "bộ", "bốn", "bớt", "bạn", "bao giờ", "bao lâu", "bao nhiêu",
        "bất cứ", "bất kì", "bất kỳ", "bất luận", "bấy", "bấy giờ",
        "bây", "bây giờ", "bấy nhiêu", "biết", "biết bao", "biết chừng nào",
        "biết đâu", "biết đâu chừng", "biết mình", "biết người",
        "buổi", "bữa", "bước", "bên", "bên cạnh", "bên ngoài",
        "bên trong", "bến", "các", "cái", "cả", "cả thảy", "cả thể",
        "cần", "càng", "căn", "cắt", "cậu", "cây", "cha", "chẳng",
        "chẳng những", "chẳng nữa", "chẳng phải", "chăng",
        "chăng nữa", "chính", "chính là", "chỉ", "chỉ có", "chỉ là",
        "chị", "chị ấy", "chịu", "chiếc", "cho", "cho đến",
        "cho đến khi", "cho nên", "cho rằng", "cho biết",
        "chớ", "chớ gì", "chớ kể", "chỗ", "chỗ này", "chốc",
        "chốc lát", "chọn", "chót", "chợt", "chủng", "chung",
        "chúng", "chúng mình", "chúng ta", "chúng tôi", "chúng ông",
        "chung quy", "chuyện", "chưa", "chưa bao giờ", "chưa kể",
        "chưa tính", "chứ", "chứ lị", "chứ còn", "chủ", "coi",
        "con", "có", "có ai", "có bao nhiêu", "có chăng", "có chăng là",
        "có khi", "có ngày", "có phải", "có thể", "có thể",
        "có điều", "có điều là", "cóc", "cô", "cô ấy", "còn",
        "còn như", "còn nữa", "còn thời gian", "cả", "cóc", "cùng",
        "cùng nhau", "cuối cùng", "cuối", "cũng", "cũng như",
        "cũng được", "cuộc", "cực", "cơ", "cứ", "cứ như", "cứ việc",
        "cực kỳ", "của", "cũng", "dạ", "dần", "dầu sao", "dẫu",
        "dẫu sao", "dẫn", "dĩ nhiên", "do", "do vì", "do đó",
        "do vậy", "dù", "dù cho", "dù gì", "dù rằng", "dù sao",
        "dùng", "dưới", "dường như", "đang", "đang khi", "đang tại",
        "đành", "đánh", "đánh đùng", "đã", "đã bao lâu", "đã từng",
        "đã rồi", "đã vậy", "đại loại", "đại để", "đầu tiên", "đầy",
        "đấy", "để", "để cho", "để mà", "đến", "đến cả", "đến giờ",
        "đến khi", "đến lúc", "đến nay", "đến như", "đến nỗi",
        "đều", "đi", "điều", "điều gì", "đích thực", "đích thị",
        "đó", "đó đây", "đôi", "đôi khi", "đổi lại", "đối với",
        "đợi", "được", "được cái", "được biết", "được rồi",
        "đương", "đương nhiên", "được", "em", "em ấy", "gì",
        "gì đó", "giờ", "giờ đây", "giờ thì", "giống", "giống như",
        "giữa", "giữ", "gần", "gần như", "gặp", "gắng", "gáì",
        "gọi", "gồm", "ha", "hai", "hai là", "hai nữa", "hẳn",
        "hẳn là", "hầu", "hết", "hết cả", "hết thảy", "hết sức",
        "hơn", "hơn nữa", "hoặc", "hoặc là", "họ", "họ đó", "là",
        "là cùng", "là nữa", "là phải", "lại", "lại còn", "lại nữa",
        "lần", "lắm", "lâu", "lâu nay", "lẽ", "lẽ nào", "lên", "lên đến",
        "lúc", "lúc khác", "lúc nào", "lúc ấy", "lúc đó", "lúc trước",
        "lúc sau", "lúc này", "lúc nào đó", "luôn", "luôn luôn",
        "lý do", "mà", "mà cả", "mà thôi", "mà lại", "mặc dù",
        "mình", "một", "một khi", "một số", "một cách", "mỗi",
        "mỗi khi", "mới", "mới hay", "mới rồi", "mọi", "mọi người",
        "mọi việc", "mọi thứ", "muốn", "mức", "nào", "nào là",
        "này", "này nọ", "nên", "nên chi", "nên chăng", "nên là",
        "nếu", "nếu có", "nếu như", "ngay", "ngay cả", "ngay khi",
        "ngay lập tức", "ngay lúc", "ngay từ", "ngày", "ngày càng",
        "ngày ngày", "ngày nay", "ngày trước", "nghe", "nghĩ",
        "nghĩa là", "người", "người ta", "ngôi", "ngọn", "ngọt",
        "ngồi", "ngộ nhỡ", "nhé", "nhiều", "nhiều khi", "nhiều lần",
        "nhưng", "nhưng mà", "như", "như ai", "như là", "như vậy",
        "như thế", "nhỉ", "nhìn", "nhất", "nhất là", "nhất định",
        "nhờ", "nhờ có", "nó", "nói", "nọ", "nơi", "nơi nào",
        "nước", "nữa", "nữa là", "phải", "phải biết", "phải chi",
        "phải chăng", "phải rồi", "phía", "phía bên", "phía dưới",
        "phía trên", "phút", "phần", "phần lớn", "phần nhiều",
        "qua", "qua khỏi", "qua lại", "quan trọng", "quá", "quá mức",
        "quá trời", "quả thật", "quả là", "quý vị", "ra", "ra sao",
        "ra thế", "ráng", "rằng", "rằng là", "rất", "rất nhiều",
        "rồi", "rồi đây", "rồi thì", "rút cục", "sang", "sao",
        "sao bằng", "sau", "sau cùng", "sau đó", "sau này", "so với",
        "song", "song le", "sớm", "số", "số là", "sự", "sự thật",
        "sự việc", "sự tình", "ta", "ta đây", "ta sẽ", "tại", "tại vì",
        "tại sao", "tất cả", "tất thảy", "tất nhiên", "tên", "thà",
        "thà rằng", "thành ra", "thành thử", "thay vì", "thật",
        "thật ra", "thật sự", "thật tình", "thấy", "thế", "thế là",
        "thế nào", "thế nào là", "thế nên", "thế ra", "thế thì",
        "theo", "thì", "thì ra", "thỉnh thoảng", "thoạt", "thoạt tiên",
        "thôi", "thời gian", "thường", "thường khi", "thường thường",
        "tuần", "tuy", "tuy là", "tuy nhiên", "tuy thế", "tuy rằng",
        "từng", "tức", "tức là", "tự", "tự nhiên", "tựu trung",
        "ủa", "và", "vẫn", "vào", "vậy", "vậy là", "vậy nên",
        "về", "về không", "việc", "việc gì", "vì", "vì chưng",
        "vì rằng", "vì sao", "với", "với lại", "với nhau",
        "vở", "vô", "vô cùng", "vừa", "vừa khi", "vừa mới",
        "xem", "xa", "xa xa", "xa xôi", "xảy ra", "xong",
        "yêu", "ý", "à", "ạ", "ừ", "ờ", "ơ", ""]
    text = read_txt(file_name)
    chunks = split_into_chunks(text)
    raw_texts = [chunk['content'] for chunk in chunks]
    vectorizer = CustomTfidfVectorizer(stop_words=word_stop).fit(raw_texts)
    tfidf_matrix = vectorizer.transform(raw_texts)
    print(f"✅ Ma trận TF-IDF đã tạo: **{tfidf_matrix.shape}**")
    name = file_name.split('.')[0]
    save_index(vectorizer, tfidf_matrix, chunks, name)

# prepare("NghiDinhThue.txt")


def bulk_prepare_and_index(directory_path, index_prefix="law_engine_full"):
    all_chunks = []
    stop_words = ["là", "thì", "của"]
    directory_path = BASE_DIR / directory_path
    # 1. Lặp qua tất cả các file .txt trong thư mục
    search_pattern = os.path.join(directory_path, "*.txt")
    file_paths = glob.glob(search_pattern)
    if not file_paths:
        print(f"❌ Không tìm thấy file .txt nào trong thư mục: {directory_path}")
        return

    print(f"✅ Bắt đầu xử lý {len(file_paths)} file luật...")

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        try:
            # Sử dụng hàm chunking đã có
            text = read_txt(file_path)
            chunks = split_into_chunks(text)
            # chunks = load_and_chunk_law_data(file_path)

            # Cập nhật metadata: Thêm tên file gốc để truy vết
            # Điều này rất quan trọng để biết chunk đó đến từ Luật nào
            for chunk in chunks:
                chunk['metadata']['source_file'] = file_name

            all_chunks.extend(chunks)
            print(f"   -> Đã chunk {len(chunks)} đoạn từ file: {file_name}")

        except Exception as e:
            print(f"   -> ⚠️ Lỗi khi xử lý file {file_name}: {e}")

    print(f"Tổng số chunks đã thu thập: {len(all_chunks)}")

    if not all_chunks:
        return

    # 2. Vector Hóa Toàn bộ Tập Dữ liệu (Dòng này gom tất cả kiến thức)
    raw_texts = [chunk['content'] for chunk in all_chunks]

    vectorizer = CustomTfidfVectorizer(stop_words=set(stop_words) if stop_words else None).fit(raw_texts)
    tfidf_matrix = vectorizer.transform(raw_texts)

    print(f"✅ Ma trận TF-IDF đã tạo với kích thước: {tfidf_matrix.shape}")

    # 3. Lưu trữ Index
    save_index(vectorizer, tfidf_matrix, all_chunks, index_prefix=index_prefix)

    print(f"🎉 Hoàn tất Indexing. Đã lưu 3 file index với prefix: {index_prefix}")
# word_stop = ["là","thì","của"]
# bulk_prepare_and_index(BASE_DIR / "data/db/law_texts", stop_words=word_stop)