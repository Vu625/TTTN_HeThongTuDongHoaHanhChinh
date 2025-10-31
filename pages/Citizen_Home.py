import streamlit as st
from services.auth_service import check_role, logout
from services.ocr_service import save_uploaded_file
from services.data_viz_service import load_forms, load_applications, save_applications
from datetime import datetime
import uuid

check_role("citizen")
st.title("🏠 Trang chủ Công dân")

menu = st.sidebar.radio("Chức năng", ["Nộp hồ sơ", "Hồ sơ đã gửi"])

if st.sidebar.button("Đăng xuất"):
    logout()

# === Nộp hồ sơ ===
if menu == "Nộp hồ sơ":
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

# === Lịch sử hồ sơ ===
if menu == "Hồ sơ đã gửi":
    st.subheader("📚 Hồ sơ của bạn")
    apps = load_applications()
    user_apps = [a for a in apps if a["citizen_id"] == st.session_state["user_id"]]

    if not user_apps:
        st.info("Bạn chưa gửi hồ sơ nào")
    else:
        for a in user_apps:
            st.write(f"""
                **Mã hồ sơ**: {a['application_id']}  
                **Loại thủ tục**: {a['form_template_id']}  
                **Tình trạng**: {a['status']}
                **Ngày gửi**: {a['submitted_at']}
                ---
            """)
