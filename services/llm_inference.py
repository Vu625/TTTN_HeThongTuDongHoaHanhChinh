#*
# File này chứa lõi logic giao tiếp trực tiếp với model AI (PhoGPT) thông qua llama-cpp-python.
# Nó chịu trách nhiệm cho việc tải model, cấu hình tham số, và chạy suy luận (inference).*#

import os
import requests  # 🆕 Thêm thư viện để gọi API LM Studio
# from rag_numpy_phogpt import RAGEngine  # ❌ COMMENT: Dòng này dùng llama-cpp, tạm thời vô hiệu khi chuyển sang LM Studio

# ===============================
# ⚙️ CẤU HÌNH ĐƯỜNG DẪN
# ===============================
#MODEL_PATH = r"PhoGPT-4B-Chat-Q4_K_M.gguf"  # ❌ Dòng này chỉ dùng khi chạy model qua llama-cpp
#DOC_FILE = r"D:\abode\pythonProject\ChatBot_Demo\data\luat_ban_hanh_vbqppl.txt"
INDEX_FOLDER = r"D:\abode\pythonProject\ChatBot_Demo\index"

# ===============================
# 🚀 KHỞI TẠO RAG + PHOGPT
# ===============================
# ❌ PHIÊN BẢN CŨ — chạy model nội bộ bằng llama-cpp
# rag_engine = RAGEngine(model_path=MODEL_PATH, n_threads=6)

# ✅ PHIÊN BẢN MỚI — dùng LM Studio API để thay thế llama-cpp
LMSTUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"  # 🆕 API của LM Studio
HEADERS = {"Content-Type": "application/json"}  # 🆕 Header cho request
# MODEL_NAME = "lmstudio-community/Meta-Llama-3-8B-Instruct"  # ⚠️ Sửa tên theo model đang chạy trong LM Studio
MODEL_NAME = "phogpt-4b-chat"  # ⚠️ Sửa tên theo model đang chạy trong LM Studio

# ===============================
# 📚 KIỂM TRA HOẶC XÂY DỰNG CHỈ MỤC
# ===============================
# ❗ RAGEngine dùng llama-cpp nên phần này chỉ giữ logic kiểm tra file
# if not os.path.exists(INDEX_FOLDER) or len(os.listdir(INDEX_FOLDER)) == 0:
#     print("⚙️ Không tìm thấy chỉ mục. (Tính năng RAG tạm thời bị vô hiệu khi dùng LM Studio)")
#     # ❌ Cũ: rag_engine.build_index_from_file(DOC_FILE, save_dir=INDEX_FOLDER)
# else:
#     print("✅ Đã tìm thấy chỉ mục. (Chưa tích hợp RAGEngine với LM Studio)")
#     # ❌ Cũ: rag_engine.load_index(INDEX_FOLDER)

# ===============================
# 💬 HÀM HỎI CHATBOT — PHIÊN BẢN MỚI
# ===============================
# def ask_lmstudio(prompt):
#     print(f"\n🧠 Câu hỏi: {prompt}\n")
#     try:
#         # 🆕 Gửi prompt tới LM Studio API (thay vì chạy model nội bộ)
#         data = {
#             "model": MODEL_NAME,
#             "messages": [
#                 {"role": "system", "content": "Bạn là chatbot hỗ trợ công dân Việt Nam, trả lời ngắn gọn và chính xác."},
#                 {"role": "user", "content": prompt}
#             ]
#         }
#
#         response = requests.post(LMSTUDIO_URL, headers=HEADERS, json=data)
#         answer = response.json()["choices"][0]["message"]["content"]
#         print(f"\n✅ Kết luận: {answer}")
#         return answer
#     except Exception as e:
#         print(f"❌ Lỗi khi gọi LM Studio API: {e}")
#         return None
from services.rag_engine import load_index,vector_search_boosted
# def ask_lmstudio(query):
#     print(f"\n🧠 Câu hỏi: {query}\n")
#     vectorizer, tfidf_matrix, loaded_chunks = load_index("NghiDinhDatDai")
#
#     retrieved_chunks = vector_search_boosted(query, vectorizer, tfidf_matrix, loaded_chunks, k=4, boost_factor=5)
#
#     print("\n--- KẾT QUẢ TRÍCH XUẤT CẢI TIẾN (BOOSTED RETRIEVAL) ---")
#     for i, res in enumerate(retrieved_chunks, start=1):
#         print(f"\nTop {i} — score boosted: {res['score_boosted']:.4f}, score original: {res['score_original']:.4f}")
#         print(res['content'])
#         print(res['metadata'])
#
#
#     context_texts = "\n".join([chunk['content'] for chunk in retrieved_chunks])
#     prompt = f"Bạn là trợ lý AI, trả lời dựa trên dữ liệu sau:\n{context_texts}\n\nCâu hỏi: {query}"
#     print(prompt)
#     try:
#         data = {
#             "model": MODEL_NAME,
#             "messages": [
#                 {"role": "system", "content": "Bạn là chatbot hỗ trợ công dân Việt Nam, trả lời ngắn gọn và chính xác."},
#                 {"role": "user", "content": prompt}
#             ]
#         }
#         response = requests.post(LMSTUDIO_URL, headers=HEADERS, json=data)
#         answer = response.json()["choices"][0]["message"]["content"]
#         print(f"\n✅ Kết luận: {answer}")
#         return answer
#     except Exception as e:
#         print(f"❌ Lỗi khi gọi LM Studio API: {e}")
#         return None
def ask_lmstudio(query):
    print(f"\n🧠 Câu hỏi: {query}\n")

    # 1. Load index đã tạo
    vectorizer, tfidf_matrix, loaded_chunks = load_index("law_engine_full")

    # 2. Trích xuất top K chunk dựa trên tìm kiếm cosine + boosting
    retrieved_chunks = vector_search_boosted(
        query,
        vectorizer,
        tfidf_matrix,
        loaded_chunks,
        k=4,            # số chunk top
        boost_factor=5  # hệ số tăng cường
    )

    # 3. In kết quả trích xuất để debug
    print("\n--- KẾT QUẢ TRÍCH XUẤT CẢI TIẾN (BOOSTED RETRIEVAL) ---")
    for i, res in enumerate(retrieved_chunks, start=1):
        meta = res['metadata']
        print(f"\nTop {i} — score boosted: {res['score_boosted']:.4f}, score original: {res['score_original']:.4f}")
        print(f"Nội dung: {res['content']}")
        print(f"Nguồn: {meta['Decree']}, {meta['Chapter']}, {meta['article_number']} - {meta['article']}, Khoản: {meta['Clause']}")

    # 4. Tạo prompt chi tiết, có metadata để LM Studio trả lời có dẫn nguồn
    context_texts = ""
    for res in retrieved_chunks:
        meta = res['metadata']
        context_texts += (
            f"[Nguồn: Nghị định: {meta['Decree']}, Chương: {meta['Chapter']}, "
            f"Điều {meta['article_number']} - {meta['article']}, Khoản: {meta['Clause']}]\n"
            f"{res['content']}\n\n"
        )

    prompt = (
        "Bạn là trợ lý AI tiếng Việt.\n"
        # "Hãy trả lời câu hỏi dựa trên dữ liệu được cung cấp dưới đây.\n"
        "Mỗi thông tin được trích dẫn phải nêu rõ Nghị định, Chương, Điều, Khoản.\n\n"
        f"--- DỮ LIỆU ---\n{context_texts}\n"
        f"--- CÂU HỎI ---\n{query}\n\n"
        "=== TRẢ LỜI CÓ DẪN NGUỒN ==="
    )

    print("\n📜 Prompt gửi tới LM Studio:")
    print(prompt)

    # 5. Gọi LM Studio API
    try:
        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "Bạn là chatbot hỗ trợ công dân Việt Nam, trả lời ngắn gọn, rõ ràng và có dẫn nguồn."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(LMSTUDIO_URL, headers=HEADERS, json=data)
        answer = response.json()["choices"][0]["message"]["content"]
        print(f"\n✅ Câu trả lời:\n{answer}")
        return answer
    except Exception as e:
        print(f"❌ Lỗi khi gọi LM Studio API: {e}")
        return None

# ===============================
# 🧑‍💻 VÒNG LẶP CHAT
# ===============================
if __name__ == "__main__":
    print("\n💬 ChatBot LM Studio sẵn sàng! Hãy đặt câu hỏi (gõ 'exit' hoặc 'thoát' để dừng).")
    while True:
        question = input("\nBạn: ").strip()
        if question.lower() in ["exit", "quit", "q", "thoát"]:
            print("👋 Tạm biệt!")
            break
        if not question:
            continue

        # ❌ Cũ: answer = ask_phogpt(question)
        # ✅ Mới: gọi API LM Studio để lấy câu trả lời
        answer = ask_lmstudio(question)

        if answer:
            print("\n🤖 LM Studio:", answer)
            print("-" * 60)
