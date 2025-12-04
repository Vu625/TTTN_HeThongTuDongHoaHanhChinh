#*
# File này chứa lõi logic giao tiếp trực tiếp với model AI (PhoGPT) thông qua llama-cpp-python.
# Nó chịu trách nhiệm cho việc tải model, cấu hình tham số, và chạy suy luận (inference).*#

import os
# import requests
#
# INDEX_FOLDER = r"D:\abode\pythonProject\ChatBot_Demo\index"
# LMSTUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
# HEADERS = {"Content-Type": "application/json"}
# MODEL_NAME = "phogpt-4b-chat"
# from services.rag_engine import load_index,vector_search_boosted
#
# def ask_lmstudio(query):
#     print(f"\n🧠 Câu hỏi: {query}\n")
#     # 1. Load index đã tạo
#     vectorizer, tfidf_matrix, loaded_chunks = load_index("law_engine_full")
#     # 2. Trích xuất top K chunk dựa trên tìm kiếm cosine + boosting
#     retrieved_chunks = vector_search_boosted(
#         query,
#         vectorizer,
#         tfidf_matrix,
#         loaded_chunks,
#         k=4,            # số chunk top
#         boost_factor=5  # hệ số tăng cường
#     )
#     # 3. In kết quả trích xuất để debug
#     print("\n--- KẾT QUẢ TRÍCH XUẤT CẢI TIẾN (BOOSTED RETRIEVAL) ---")
#     for i, res in enumerate(retrieved_chunks, start=1):
#         meta = res['metadata']
#         print(f"\nTop {i} — score boosted: {res['score_boosted']:.4f}, score original: {res['score_original']:.4f}")
#         print(f"Nội dung: {res['content']}")
#         print(f"Nguồn: {meta['Decree']}, {meta['Chapter']}, {meta['article_number']} - {meta['article']}, Khoản: {meta['Clause']}")
#     context_texts = ""
#     for res in retrieved_chunks:
#         meta = res['metadata']
#         context_texts += (
#             f"[Nguồn: Nghị định: {meta['Decree']}, Chương: {meta['Chapter']}, "
#             f"Điều {meta['article_number']} - {meta['article']}, Khoản: {meta['Clause']}]\n"
#             f"{res['content']}\n\n"
#         )
#     prompt = (
#         "Bạn là trợ lý AI tiếng Việt.\n"
#         "Mỗi thông tin được trích dẫn phải nêu rõ Nghị định, Chương, Điều, Khoản.\n\n"
#         f"--- DỮ LIỆU ---\n{context_texts}\n"
#         f"--- CÂU HỎI ---\n{query}\n\n"
#         "=== TRẢ LỜI CÓ DẪN NGUỒN ==="
#     )
#
#     print("\n📜 Prompt gửi tới LM Studio:")
#     print(prompt)
#
#     # 5. Gọi LM Studio API
#     try:
#         data = {
#             "model": MODEL_NAME,
#             "messages": [
#                 {"role": "system", "content": "Bạn là chatbot hỗ trợ công dân Việt Nam, trả lời ngắn gọn, rõ ràng và có dẫn nguồn."},
#                 {"role": "user", "content": prompt}
#             ]
#         }
#         response = requests.post(LMSTUDIO_URL, headers=HEADERS, json=data)
#         answer = response.json()["choices"][0]["message"]["content"]
#         print(f"\n✅ Câu trả lời:\n{answer}")
#         return answer
#     except Exception as e:
#         print(f"❌ Lỗi khi gọi LM Studio API: {e}")
#         return None
#
# # ===============================
# # 🧑‍💻 VÒNG LẶP CHAT
# # ===============================
# if __name__ == "__main__":
#     print("\n💬 ChatBot LM Studio sẵn sàng! Hãy đặt câu hỏi (gõ 'exit' hoặc 'thoát' để dừng).")
#     while True:
#         question = input("\nBạn: ").strip()
#         if question.lower() in ["exit", "quit", "q", "thoát"]:
#             print("👋 Tạm biệt!")
#             break
#         if not question:
#             continue
#
#         # ❌ Cũ: answer = ask_phogpt(question)
#         # ✅ Mới: gọi API LM Studio để lấy câu trả lời
#         answer = ask_lmstudio(question)
#
#         if answer:
#             print("\n🤖 LM Studio:", answer)
#             print("-" * 60)

import os
import requests
from dotenv import load_dotenv
from google import genai

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy khóa từ biến môi trường đã tải
api_key = os.getenv("GEMINI_API_KEY")

# if api_key:
#     client = genai.Client(api_key=api_key)


# Lấy khóa từ biến môi trường đã tải
# api_key = os.getenv("GEMINI_API_KEY")
# --- 1. CẤU HÌNH CHUNG ---

# Thư mục index và các cấu hình RAG khác
INDEX_FOLDER = r"D:\abode\pythonProject\ChatBot_Demo\index"
from services.rag_engine import load_index, vector_search_boosted

# Cấu hình LM STUDIO (PhoGPT)
LMSTUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
HEADERS = {"Content-Type": "application/json"}
MODEL_NAME_LMSTUDIO = "phogpt-4b-chat"  # Đổi tên biến để rõ ràng hơn

# --- 2. KHỞI TẠO GEMINI CLIENT ---
# Client sẽ tự động lấy GOOGLE_API_KEY từ biến môi trường
try:
    gemini_client = genai.Client(api_key=api_key)
    print("✅ Gemini Client khởi tạo thành công.")
except Exception as e:
    print(f"❌ Lỗi khởi tạo Gemini Client (Kiểm tra GOOGLE_API_KEY): {e}")
    gemini_client = None


# --- 3. HÀM HỖ TRỢ GỌI LM STUDIO ---
def _call_lmstudio_api(prompt):
    """Gửi prompt RAG tới LM Studio (PhoGPT)"""
    try:
        data = {
            "model": MODEL_NAME_LMSTUDIO,
            "messages": [
                {"role": "system",
                 "content": "Bạn là chatbot hỗ trợ công dân Việt Nam, trả lời ngắn gọn, rõ ràng và có dẫn nguồn."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(LMSTUDIO_URL, headers=HEADERS, json=data, timeout=60)
        response.raise_for_status()  # Báo lỗi nếu mã trạng thái không thành công
        answer = response.json()["choices"][0]["message"]["content"]
        return answer
    except requests.exceptions.RequestException as e:
        # Lỗi kết nối hoặc HTTP
        return f"❌ Lỗi khi gọi LM Studio API. Vui lòng kiểm tra LM Studio có đang chạy không: {e}"
    except Exception as e:
        # Lỗi xử lý JSON hoặc lỗi khác
        return f"❌ Lỗi xử lý phản hồi từ LM Studio: {e}"


# --- 4. HÀM HỖ TRỢ GỌI GEMINI API ---
def _call_gemini_api(prompt):
    """Gửi prompt RAG tới Gemini API"""
    global gemini_client
    if gemini_client is None:
        return "❌ Gemini Client chưa được khởi tạo. Vui lòng kiểm tra GOOGLE_API_KEY."

    try:
        # Sử dụng mô hình mạnh mẽ cho tác vụ RAG
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',  # Hoặc gemini-2.5-flash nếu muốn tốc độ cao hơn
            contents=prompt,
            config={
                # System instruction để mô hình trả lời theo yêu cầu RAG
                "system_instruction": "Bạn là trợ lý AI tiếng Việt chuyên nghiệp. Trả lời các câu hỏi dựa trên DỮ LIỆU đã cung cấp. Phải trích dẫn rõ ràng Nghị định, Chương, Điều, Khoản cho mỗi thông tin được cung cấp.",
                # Đặt nhiệt độ thấp cho tác vụ RAG cần tính chính xác
                "temperature": 0.1
            }
        )
        return response.text
    except Exception as e:
        print(f"❌ Lỗi khi gọi Gemini API: {e}")
        return f"❌ Lỗi khi gọi Gemini API: {e}"


# --- 5. HÀM CHÍNH ĐIỀU KHIỂN RAG VÀ CHUYỂN ĐỔI MÔ HÌNH ---
def ask_rag(query, model_choice="LMSTUDIO"):
    """
    Thực hiện truy vấn RAG và chuyển đổi giữa các mô hình LLM.

    :param query: Câu hỏi của người dùng.
    :param model_choice: "LMSTUDIO" (mặc định) hoặc "GEMINI".
    :return: Câu trả lời từ mô hình đã chọn.
    """
    print(f"\n🧠 Câu hỏi: {query}")
    print(f"🎯 Mô hình được chọn: {model_choice}")

    # 1. Load index đã tạo
    vectorizer, tfidf_matrix, loaded_chunks = load_index("law_engine_full")

    # 2. Trích xuất top K chunk dựa trên tìm kiếm cosine + boosting
    retrieved_chunks = vector_search_boosted(
        query,
        vectorizer,
        tfidf_matrix,
        loaded_chunks,
        k=4,  # số chunk top
        boost_factor=5  # hệ số tăng cường
    )

    # 3. Tạo context và prompt (Giữ nguyên logic RAG)
    print("\n--- KẾT QUẢ TRÍCH XUẤT (RAG RETRIEVAL) ---")
    context_texts = ""
    for i, res in enumerate(retrieved_chunks, start=1):
        meta = res['metadata']
        print(f"Top {i} — score boosted: {res['score_boosted']:.4f}")
        print(f"Nguồn: {meta['Decree']}, {meta['article_number']} - {meta['article']}")
        context_texts += (
            f"[Nguồn: Nghị định: {meta['Decree']},  {meta['Chapter']}, "
            f" {meta['article_number']} - {meta['article']}, Khoản: {meta['Clause']}]\n"
            f"{res['content']}\n\n"
        )

    prompt = (
        "Bạn là trợ lý AI tiếng Việt.\n"
        "Mỗi thông tin được trích dẫn phải nêu rõ Nghị định, Chương, Điều, Khoản.\n\n"
        f"--- DỮ LIỆU ---\n{context_texts}\n"
        f"--- CÂU HỎI ---\n{query}\n\n"
        "=== TRẢ LỜI CÓ DẪN NGUỒN ==="
    )
    print(prompt)
    print("\n📜 Prompt gửi tới LLM đã tạo xong.")

    # 4. Gọi API của Mô hình đã chọn
    answer = ""
    if model_choice == "GEMINI":
        print("🚀 Đang gọi Gemini API...")
        answer = _call_gemini_api(prompt)
    elif model_choice == "LMSTUDIO":
        print("💻 Đang gọi LM Studio API (PhoGPT)...")
        answer = _call_lmstudio_api(prompt)
    else:
        answer = f"Lựa chọn mô hình '{model_choice}' không hợp lệ. Chỉ hỗ trợ 'LMSTUDIO' hoặc 'GEMINI'."

    print(f"\n✅ Câu trả lời từ {model_choice}:\n{answer}")
    return answer

# --- VÍ DỤ CÁCH GỌI ---
# print("\n==================================")
# print("KỊCH BẢN 1: GỌI LM STUDIO (Mặc định)")
# ask_rag("Các hành vi nào bị nghiêm cấm trong hoạt động xây dựng?", model_choice="LMSTUDIO")

# print("\n==================================")
# print("KỊCH BẢN 2: GỌI GEMINI")
# ask_rag("Các hành vi nào bị nghiêm cấm trong hoạt động xây dựng?", model_choice="GEMINI")