#*
# File này chứa lõi logic giao tiếp trực tiếp với model AI (PhoGPT) thông qua llama-cpp-python.
# Nó chịu trách nhiệm cho việc tải model, cấu hình tham số, và chạy suy luận (inference).*#

# services/llm_inference.py

import os
import pickle
import numpy as np
import requests
from pathlib import Path
from scipy.sparse.linalg import norm as sparse_norm
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai.errors import APIError

# ===============================
# Cấu hình LM Studio (Giữ nguyên)
# ===============================
# LMSTUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
# HEADERS = {"Content-Type": "application/json"}
GEMINI_API_KEY = "AIzaSyAkG6c4FmDIM72G5tTYEvevgi7SN4UGowU"
GEMINI_MODEL = "gemini-2.5-flash" # Mô hình mạnh mẽ và nhanh chóng

try:
    # Khởi tạo Client Gemini
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    print("✅ Đã khởi tạo Gemini Client cho Generation.")
except Exception as e:
    print(f"❌ Lỗi khởi tạo Gemini Client: {e}")
    gemini_client = None
# ===============================
# Cấu hình SBERT (Tải lại mô hình)
# ===============================
# Đường dẫn thư mục index (Cần xác định tương đối từ file này)
BASE_DIR = Path(__file__).resolve().parent.parent

# Khởi tạo lại SBERT model cho Query (phải khớp với model dùng để index)
try:
    SBERT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    query_sbert_model = SentenceTransformer(SBERT_MODEL_NAME)
    print(f"✅ Đã tải SBERT Model cho Query.")
except Exception as e:
    print(f"❌ Lỗi tải SBERT Model cho Query: {e}")
    query_sbert_model = None


# ===============================
# 1️⃣ Hàm Load Database
# ===============================
def load_vector_database(index_prefix):
    """Tải tất cả các thành phần index đã lưu bởi rag_engine."""
    index_path = BASE_DIR / "data/index"

    try:
        # Tải SBERT Embeddings và Chunks (tên file mới)
        embeddings = np.load(index_path / f"{index_prefix}_embeddings.npy")
        with open(index_path / f"{index_prefix}_chunks.pkl", "rb") as f:
            chunks = pickle.load(f)
        with open(index_path / f"{index_prefix}_filemap.pkl", "rb") as f:
            filemap = pickle.load(f)

        # Tải TF-IDF components
        from scipy.sparse import load_npz  # Đảm bảo dòng này đã được import ở đầu file

        tfidf_matrix = load_npz(index_path / f"{index_prefix}_tfidf.npz")
        with open(index_path / f"{index_prefix}_vectorizer.pkl", "rb") as f:
            vectorizer = pickle.load(f)

        return {
            'embeddings': embeddings,
            'chunks': chunks,
            'filemap': filemap,
            'tfidf_matrix': tfidf_matrix,
            'vectorizer': vectorizer
        }

    except FileNotFoundError as e:
        print(f"❌ Lỗi: Không tìm thấy file index. Đảm bảo đã chạy rag_engine.py. Lỗi: {e}")
        return None
    except Exception as e:
        print(f"❌ Lỗi tải database: {e}")
        return None


# ===============================
# 2️⃣ Hàm Tìm kiếm (Boosted Search)
# ===============================
def vector_search_boosted(
        query,
        embeddings,
        chunks,
        vectorizer,
        tfidf_matrix,
        k=4,
        boost_factor=5
):
    """
    Tìm kiếm kết hợp giữa Cosine Similarity (SBERT) và TF-IDF (Lexical).
    """
    if query_sbert_model is None:
        raise ConnectionError("Mô hình SBERT chưa được tải.")

    # A) SBERT Search (Semantic/Ngữ nghĩa)
    query_embedding = query_sbert_model.encode([query], convert_to_tensor=False)[0]

    # Tính cosine similarity giữa query và tất cả chunks
    semantic_scores = cosine_similarity([query_embedding], embeddings)[0]

    # B) TF-IDF Search (Lexical/Từ khóa)
    query_tfidf = vectorizer.transform([query])
    # Tính cosine similarity TF-IDF
    lexical_scores = cosine_similarity(query_tfidf, tfidf_matrix)[0]

    # C) Kết hợp điểm số (Boosted)
    # Chuẩn hóa điểm số (max-min normalization)
    norm_semantic = (semantic_scores - semantic_scores.min()) / (semantic_scores.max() - semantic_scores.min())
    norm_lexical = (lexical_scores - lexical_scores.min()) / (lexical_scores.max() - lexical_scores.min())

    # Kết hợp (Boosted): Semantic + (Lexical * Boost Factor)
    final_scores = norm_semantic + (norm_lexical * boost_factor)

    # D) Lấy top K
    top_indices = np.argsort(final_scores)[::-1][:k]

    results = []
    for i in top_indices:
        # Giả định chunks là list các chuỗi, ta cần metadata
        # (Vì trong rag_engine cũ chunks là list dict, ta cần metadata được nhúng lại)
        # Trong code SBERT cuối cùng, chunks là list chuỗi, cần sửa lại để lưu metadata
        # Tạm thời ta chỉ lấy nội dung nếu metadata bị thiếu.

        # Nếu chunks là list các dict (như code ban đầu)
        if isinstance(chunks[i], dict):
            results.append(chunks[i])
        else:  # Nếu chunks chỉ là list chuỗi (như code SBERT đã sửa)
            # Ta cần sửa lại rag_engine.py để lưu metadata. Tạm thời chỉ lấy content
            results.append({'content': chunks[i],
                            'metadata': {'Decree': 'Không rõ', 'Chapter': 'Không rõ', 'article_number': 'N/A',
                                         'article': 'N/A', 'Clause': 'N/A'}})

    # 🚨 LƯU Ý QUAN TRỌNG: CẦN SỬA LẠI HÀM prepare_index_for_folder TRONG rag_engine.py
    # ĐỂ NÓ LƯU METADATA CÙNG VỚI CHUNK NỘI DUNG.
    # Hiện tại tôi đang sử dụng dữ liệu giả định nếu metadata bị thiếu.

    return results


# ===============================
# Hàm hỏi RAG + LM (ask_rag)
# ===============================
def ask_rag(prompt, model_choice="phogpt-4b-chat"):
    """
    Trả lời câu hỏi dựa trên dữ liệu luật đã index bằng RAG + LM Studio.
    """
    # 1️⃣ Load vector database
    vector_db = load_vector_database("law_engine_full")
    if vector_db is None:
        return "Xin lỗi, không thể tải database vector. Vui lòng kiểm tra file index."

    # Lấy các thành phần SBERT và TF-IDF
    embeddings = vector_db['embeddings']
    chunks = vector_db['chunks']
    tfidf_matrix = vector_db['tfidf_matrix']
    vectorizer = vector_db['vectorizer']

    # 2️⃣ Tìm top-k chunks với boosted search
    top_k_chunks = vector_search_boosted(
        prompt,
        embeddings=embeddings,
        chunks=chunks,
        vectorizer=vectorizer,
        tfidf_matrix=tfidf_matrix,
        k=4,
        boost_factor=5
    )

    if not top_k_chunks:
        return "Xin lỗi, tôi không tìm thấy thông tin phù hợp."

    # 3️⃣ Ghép ngữ cảnh vào prompt
    context_texts = ""
    for res in top_k_chunks:
        meta = res.get('metadata', {})

        # Sử dụng thông tin metadata nếu có, nếu không thì dùng placeholder
        decree = meta.get('Decree', 'N/A')
        chapter = meta.get('Chapter', 'N/A')
        article_num = meta.get('article_number', 'N/A')
        article = meta.get('article', 'N/A')
        clause = meta.get('Clause', 'N/A')

        context_texts += (
            f"[Nguồn: Nghị định: {decree}, Chương: {chapter}, "
            f"Điều {article_num} - {article}, Khoản: {clause}]\n"
            f"{res['content']}\n\n"
        )

    full_prompt = (
        "Bạn là trợ lý AI tiếng Việt.\n"
        "Mỗi thông tin được trích dẫn phải nêu rõ Nghị định, Chương, Điều, Khoản.\n\n"
        f"--- DỮ LIỆU ---\n{context_texts}\n"
        f"--- CÂU HỎỎI ---\n{prompt}\n\n"
        "=== TRẢ LỜI CÓ DẪN NGUỒN ==="
    )

    # 4️⃣ Gọi gemini API
    if gemini_client is None:
        return "Xin lỗi, Gemini Client chưa được khởi tạo. Không thể tạo câu trả lời."

    try:
        # 1. Định dạng prompt thành cấu trúc contents cho generate_content
        # Đây là cách gọi tiêu chuẩn và ổn định nhất

        # Tạo danh sách các phần nội dung, bỏ qua vai trò (role) hệ thống trong hàm này.
        # Hoặc truyền trực tiếp messages (tùy thuộc phiên bản SDK, generate_content thường thích nội dung trực tiếp)

        # Phương án an toàn nhất: Đưa System Prompt vào đầu User Prompt
        full_prompt_for_api = (
                "Bạn là chatbot hỗ trợ công dân Việt Nam, trả lời ngắn gọn, rõ ràng và có dẫn nguồn.\n\n"
                + full_prompt
        )

        # Gọi API tạo nội dung (generation)
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[full_prompt_for_api],  # Truyền nội dung dưới dạng List[str]
            # Có thể thêm cấu hình:
            # config=genai.types.GenerateContentConfig(
            #     system_instruction="Bạn là chatbot hỗ trợ công dân Việt Nam, trả lời ngắn gọn, rõ ràng và có dẫn nguồn."
            # )
        )

        # Trích xuất câu trả lời
        answer = response.text
        return answer

    except APIError as e:
        print(f"❌ Lỗi API Gemini: {e}")
        return "Xin lỗi, có lỗi xảy ra khi gọi Gemini API."
    except Exception as e:
        print(f"❌ Lỗi không xác định khi gọi Gemini: {e}")
        return "Xin lỗi, có lỗi xảy ra khi kết nối Gemini."


# ===============================
# Thử nghiệm hàm
# ===============================
if __name__ == "__main__":
    print("--- CHẠY THỬ NGHIỆM RAG ---")

    # 🚨 BẠN PHẢI CHẠY LM STUDIO TRƯỚC KHI CHẠY PHẦN NÀY 🚨
    # Khởi chạy một mô hình (ví dụ: phogpt-4b-chat) trên http://127.0.0.1:1234

    test_prompt = "Thủ tục thu hồi đất đối với các hộ gia đình, cá nhân được quy định như thế nào?"

    # LƯU Ý: Nếu LM Studio chưa chạy, phần này sẽ lỗi.
    # Nếu code chạy tốt, nó sẽ in ra câu trả lời từ LLM
    try:
        answer = ask_rag(test_prompt)
        print(f"\n[CÂU HỎI]: {test_prompt}\n")
        print(f"[TRẢ LỜI LLM]:\n{answer}")
    except Exception as e:
        print(f"\n[KHÔNG THỂ CHẠY HỆ THỐNG]: {e}")
        print("Vui lòng kiểm tra LM Studio đang chạy và đã tải mô hình.")

