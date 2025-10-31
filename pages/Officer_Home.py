# import streamlit as st
# from services.auth_service import check_role, logout
# from services.data_viz_service import load_applications
#
# check_role("officer")
# if st.sidebar.button("Đăng xuất"):
#     logout()
# st.title("📥 Danh sách hồ sơ chờ xử lý")
#
# apps = load_applications()
#
# if not apps:
#     st.info("Chưa có hồ sơ nào")
# else:
#     for a in apps:
#         st.write(f"""
#             **Mã hồ sơ**: {a['application_id']}
#             **Người nộp**: {a['citizen_id']}
#             **Thủ tục**: {a['form_template_id']}
#             **Ngày gửi**: {a['submitted_at']}
#             **Trạng thái**: {a['status']}
#         """)


import streamlit as st
from services.auth_service import check_role
from services.data_viz_service import load_applications, save_applications
from services.ocr_service import extract_text
from pathlib import Path

check_role("officer")
st.title("🧾 Xử lý hồ sơ công dân")
#from models.ocr.tessdata import config
# try:
#     from . import config # Giả định cấu trúc thư mục
#     # Hoặc đảm bảo config được chạy ở điểm khởi đầu ứng dụng
# except ImportError:
#     # Xử lý nếu cấu hình không tìm thấy, nhưng trong dự án này nên là bắt buộc
#     pass

apps = load_applications()

if not apps:
    st.info("Chưa có hồ sơ nào được gửi")
else:
    selected = st.selectbox(
        "Chọn hồ sơ cần xem:",
        options=[f"{a['application_id']} - {a['form_template_id']}" for a in apps]
    )

    app = next(a for a in apps if a['application_id'] in selected)

    st.write(f"**Người nộp:** {app['citizen_id']}")
    st.write(f"**Loại thủ tục:** {app['form_template_id']}")
    st.write(f"**Ngày gửi:** {app['submitted_at']}")
    st.write(f"**Trạng thái hiện tại:** {app['status']}")
    st.divider()

    st.subheader("📎 Tài liệu đính kèm")

    for doc_path in app["documents"]:
        path = Path(doc_path)
        if not path.exists():
            st.warning(f"Không tìm thấy file: {path}")
            continue

        st.image(str(path), caption=path.name, width=400)
        if st.button(f"🔍 Chạy OCR cho {path.name}"):
            text = extract_text(path)
            st.text_area(f"Nội dung OCR ({path.name})", text, height=200)
            if "ocr_texts" not in app:
                app["ocr_texts"] = {}
            app["ocr_texts"][path.name] = text

    st.divider()
    new_status = st.selectbox(
        "Cập nhật trạng thái hồ sơ:",
        options=["submitted", "verifying", "approved", "rejected"],
        index=["submitted", "verifying", "approved", "rejected"].index(app["status"])
    )

    if st.button("💾 Lưu cập nhật"):
        app["status"] = new_status
        save_applications(apps)
        st.success("Đã lưu trạng thái mới!")
