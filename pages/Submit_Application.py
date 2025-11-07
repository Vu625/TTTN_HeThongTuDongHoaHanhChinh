import streamlit as st
from services.auth_service import check_role, logout
from services.ocr_service import save_uploaded_file
from services.rag_engine import generate_answer
from services.data_viz_service import load_forms, load_applications, save_applications, get_workflow_for_procedure, get_name_form
from datetime import datetime
import uuid
from services.layout import load_common_layout
from services.auth_service import check_role
# check_role("citizen")
page = load_common_layout()
# check_role("citizen")
st.title("🏠 Nộp Hồ Sơ")

# menu = st.sidebar.radio("Chức năng", ["Hồ sơ đã gửi", "💬 Chatbot Hành chính AI"])

# === ChatBot ===
# if menu == "💬 Chatbot Hành chính AI":
#     st.subheader("💬 Hỏi đáp thủ tục hành chính thông minh")
#     st.write("Bạn có thể hỏi như:")
#     st.info("• Tôi muốn cấp lại CCCD thì cần gì?\n• Đăng ký khai sinh trong bao lâu?\n• Hồ sơ chứng thực gồm gì?")
#
#     user_input = st.text_input("Nhập câu hỏi của bạn:")
#     if st.button("Gửi câu hỏi") and user_input.strip():
#         with st.spinner("Đang tra cứu văn bản pháp luật..."):
#             answer = generate_answer(user_input)
#         st.success("Kết quả:")
#         st.markdown(answer)



st.subheader("📄 Chọn thủ tục")

forms = load_forms()
form_titles = [f["name_vn"] for f in forms]
selection = st.selectbox("Thủ tục:", form_titles)

if selection:
        form = next(f for f in forms if f["name_vn"] == selection)
        req_doc = ""
        for field in form["required_doc"]:
            req_doc += field + ", "

        st.write(f"📌 Tải tài liệu bắt buộc:{req_doc}")
        uploaded_files = st.file_uploader("Chọn file", accept_multiple_files=True)

        st.write("📝 Điền thông tin:")
        form_data = {}
        for field in form["required_fields"]:
            form_data[field["name"]] = st.text_input(field["label"])

        if st.button("Gửi hồ sơ"):
            apps = load_applications()
            saved_files = [save_uploaded_file(f) for f in uploaded_files]
            new_app = {
                "application_id": str(uuid.uuid4()),
                "citizen_id": st.session_state["user_id"],
                "form_template_id": form["form_template_id"],
                "status": "submitted",
                "submitted_at": datetime.now().isoformat(),
                "documents": saved_files,
                "form_data": form_data
            }
            apps.append(new_app)
            save_applications(apps)
            st.success("🎉 Gửi hồ sơ thành công!")
