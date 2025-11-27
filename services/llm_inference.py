#*
# File này chứa lõi logic giao tiếp trực tiếp với model AI (PhoGPT) thông qua llama-cpp-python.
# Nó chịu trách nhiệm cho việc tải model, cấu hình tham số, và chạy suy luận (inference).*#

import os
import requests

INDEX_FOLDER = r"D:\abode\pythonProject\ChatBot_Demo\index"

LMSTUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
HEADERS = {"Content-Type": "application/json"}
MODEL_NAME = "phogpt-4b-chat"
from services.rag_engine import load_index,vector_search_boosted

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
