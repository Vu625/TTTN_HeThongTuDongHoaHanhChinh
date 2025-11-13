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
if not os.path.exists(INDEX_FOLDER) or len(os.listdir(INDEX_FOLDER)) == 0:
    print("⚙️ Không tìm thấy chỉ mục. (Tính năng RAG tạm thời bị vô hiệu khi dùng LM Studio)")
    # ❌ Cũ: rag_engine.build_index_from_file(DOC_FILE, save_dir=INDEX_FOLDER)
else:
    print("✅ Đã tìm thấy chỉ mục. (Chưa tích hợp RAGEngine với LM Studio)")
    # ❌ Cũ: rag_engine.load_index(INDEX_FOLDER)

# ===============================
# 💬 HÀM HỎI CHATBOT — PHIÊN BẢN MỚI
# ===============================
def ask_lmstudio(prompt):
    print(f"\n🧠 Câu hỏi: {prompt}\n")
    try:
        # 🆕 Gửi prompt tới LM Studio API (thay vì chạy model nội bộ)
        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "Bạn là chatbot hỗ trợ công dân Việt Nam, trả lời ngắn gọn và chính xác."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(LMSTUDIO_URL, headers=HEADERS, json=data)
        answer = response.json()["choices"][0]["message"]["content"]
        print(f"\n✅ Kết luận: {answer}")
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
