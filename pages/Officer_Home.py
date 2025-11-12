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
from services.data_viz_service import load_applications, save_applications, get_workflow_for_procedure , user_full_name , get_name_form
from pathlib import Path
from services.workflow_service import ACTIONS


# st.title("🧾 Xử lý hồ sơ công dân")

# apps = load_applications()
#
# if not apps:
#     st.info("Chưa có hồ sơ nào được gửi")
# else:
#     selected = st.selectbox(
#         "Chọn hồ sơ cần xem:",
#         options=[f"{a['application_id']} - {a['form_template_id']}" for a in apps]
#     )
#
#     app = next(a for a in apps if a['application_id'] in selected)
#
#     st.write(f"**Người nộp:** {app['citizen_id']}")
#     st.write(f"**Loại thủ tục:** {app['form_template_id']}")
#     st.write(f"**Ngày gửi:** {app['submitted_at']}")
#     st.write(f"**Trạng thái hiện tại:** {app['status']}")
#     st.divider()
#
#     st.subheader("📎 Tài liệu đính kèm")
#
#     for doc_path in app["documents"]:
#         path = Path(doc_path)
#         if not path.exists():
#             st.warning(f"Không tìm thấy file: {path}")
#             continue
#
#         st.image(str(path), caption=path.name, width=400)
#         if st.button(f"🔍 Chạy OCR cho {path.name}"):
#             text = extract_text(path)
#             st.text_area(f"Nội dung OCR ({path.name})", text, height=200)
#             if "ocr_texts" not in app:
#                 app["ocr_texts"] = {}
#             app["ocr_texts"][path.name] = text
#
#     st.divider()
#     new_status = st.selectbox(
#         "Cập nhật trạng thái hồ sơ:",
#         options=["submitted", "verifying", "approved", "rejected"],
#         index=["submitted", "verifying", "approved", "rejected"].index(app["status"])
#     )
#
#     if st.button("💾 Lưu cập nhật"):
#         app["status"] = new_status
#         save_applications(apps)
#         st.success("Đã lưu trạng thái mới!")



# apps = load_applications()
# if not apps:
#     st.info("Chưa có hồ sơ nào được gửi")
# else:
#     selected = st.selectbox(
#         "Chọn hồ sơ cần xem:",
#         options=[f"{a['application_id']} - {a['form_template_id']}" for a in apps]
#     )
#     app = next(a for a in apps if a['application_id'] in selected)
#     steps = get_workflow_for_procedure(app["workflow_id"])
#     current_step = app.get("current_step", 1)
#     st.subheader(f"🪜 Bước hiện tại: {steps[current_step-1]['title']} ({current_step}/{len(steps)})")
#
#     st.write(f"**Người nộp:** {app['citizen_id']}")
#     st.write(f"**Trạng thái:** {app['status']}")
#     st.divider()
#
#     if current_step < len(steps):
#         next_title = steps[current_step]["title"]
#         if st.button(f"✅ Hoàn tất bước '{steps[current_step-1]['title']}' / chuyển sang '{next_title}'"):
#             app["current_step"] = current_step + 1
#             app["status"] = "verifying" if current_step < len(steps)-1 else "approved"
#             save_applications(apps)
#             st.success(f"Đã chuyển hồ sơ sang bước '{next_title}'")
#             st.rerun()
#     else:
#         st.success("🎉 Hồ sơ đã hoàn thành toàn bộ quy trình!")


# apps = load_applications()
#
# if not apps:
#     st.info("Chưa có hồ sơ nào được gửi")
# else:
#     selected = st.selectbox(
#         "Chọn hồ sơ cần xem:",
#         options=[f"{a['application_id']} - {get_name_form(a['form_template_id'])}" for a in apps]
#     )
#
#     app = next(a for a in apps if a['application_id'] in selected)
#     steps = get_workflow_for_procedure(app["form_template_id"])
#     current_step = app.get("current_step", 1)
#     step_data = steps[current_step - 1]
#     st.subheader(f"🪜 Bước {current_step}/{len(steps)}: {step_data['title']}")
#     st.write(f"**Người nộp:** {user_full_name(app['citizen_id'])}")
#     st.write(f"**Trạng thái:** {app['status']}")
#     st.divider()
#
#     # === Gọi hành động tương ứng ===
#     action_name = step_data.get("action")
#     if action_name and action_name in ACTIONS:
#         app = ACTIONS[action_name](app)
#     else:
#         st.info("Không có hành động đặc biệt cho bước này.")
#
#     st.divider()
#
#     # === Điều hướng workflow ===
#     if current_step < len(steps):
#         next_title = steps[current_step]["title"]
#         if st.button(f"➡️ Chuyển sang '{next_title}'"):
#             app["current_step"] = current_step + 1
#             save_applications(apps)
#             st.success(f"Đã chuyển sang bước '{next_title}'")
#             st.rerun()
#     else:
#         st.success("🎉 Hồ sơ đã hoàn tất toàn bộ quy trình!")



# from services.layout import load_common_layout
# page = load_common_layout()
import streamlit as st

# 🧭 1. Thanh tiêu đề (Header)
def header(username):
    st.markdown(
        """
        <style>
        .header {
            background-color: #004D40; /* xanh đậm */
            padding: 10px 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: white;
            border-bottom: 4px solid #80CBC4;
        }
        .header-left {
            display: flex;
            align-items: center;
        }
        .header-left img {
            width: 55px;
            margin-right: 10px;
        }
        .header-center img {
            width: 380px;
            border-radius: 10px;
        }
        .header-right {
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 16px;
        }
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: white;
            color: #004D40;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .menu {
            background-color: #E6F2FF;
            padding: 10px;
            text-align: center;
        }
        .menu a {
            text-decoration: none;
            color: #0055A5;
            margin: 0 15px;
            font-weight: 600;
        }
        .menu a:hover {
            color: #FFB400;
            
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="header">
            <div class="header-left">
                <img src="https://upload.wikimedia.org/wikipedia/commons/2/21/Coat_of_arms_of_Vietnam.svg">
                <div>
                    <div style="font-weight:bold; font-size:18px;">BỘ CÔNG AN</div>
                    <div style="font-size:14px;">TRUNG TÂM DỮ LIỆU QUỐC GIA VỀ DÂN CƯ</div>
                </div>
            </div>
            <div class="header-center">
                <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Vietnam_Halong_Bay_banner.jpg/800px-Vietnam_Halong_Bay_banner.jpg">
            </div>
            <div class="header-right">
                <span>🔔</span>
                <span>{username}</span>
                <div class="avatar">👮‍♂️</div>
            </div>
        </div>
        <div class="menu">
        <a href="/">Trang chủ</a>
        <a href="/Giới_thiệu">Giới thiệu</a>
        <a href="/Tin_tức">Tin tức</a>
        <a href="/Văn_bản_pháp_lý">Văn bản pháp lý</a>
        <a href="/Hỏi_đáp">Hỏi đáp</a>
    </div>
        """,
        unsafe_allow_html=True,
    )

# 📂 2. Thanh điều hướng bên trái
def sidebar():
    st.sidebar.title("📋 Danh mục chức năng")
    page = st.sidebar.radio(
        "Chọn trang:",
        [
            "🏠 Trang chủ",
            "🧾 Duyệt hồ sơ công dân",
            "📊 Thống kê dân số",
            "📰 Tin tức & cảnh báo",
            "⚙️ Cài đặt hệ thống",
        ],
        label_visibility="collapsed"
    )
    return page

# 💬 3. Nội dung chính cho từng trang
def main_content(page):
    full_name = st.session_state["full_name"]

    if page == "🏠 Trang chủ":
        st.markdown(f"<h2>👋 Xin chào, {full_name}</h2>", unsafe_allow_html=True)
        st.info("Chào mừng bạn đến với cổng thông tin quản lý dân cư của Bộ Công an.")

    elif page == "🧾 Duyệt hồ sơ công dân":
        st.switch_page('pages/Handle_Application.py')
        # st.markdown("## 🧾 Duyệt hồ sơ công dân")
        # st.write("Danh sách hồ sơ chờ duyệt:")
        # st.table([
        #     {"Mã hồ sơ": "HS001", "Họ tên": "Nguyễn Văn A", "Trạng thái": "Chờ duyệt"},
        #     {"Mã hồ sơ": "HS002", "Họ tên": "Trần Thị B", "Trạng thái": "Chờ duyệt"},
        # ])
        # if st.button("✅ Duyệt tất cả"):
        #     st.success("Tất cả hồ sơ đã được duyệt thành công.")

    elif page == "📊 Thống kê dân số":
        st.markdown("## 📊 Thống kê dân số toàn quốc")
        st.metric(label="Tổng dân số", value="98.7 triệu người")
        st.metric(label="Tỷ lệ nam/nữ", value="49.3% / 50.7%")
        st.metric(label="Số công dân mới đăng ký", value="+12,345 trong tháng 10")
        st.bar_chart({"Nam": [49.3], "Nữ": [50.7]})

    elif page == "📰 Tin tức & cảnh báo":
        st.markdown("## 📰 Tin tức và cảnh báo")
        st.info("🔔 Bộ Công an triển khai chiến dịch tuyên truyền về bảo mật định danh cá nhân.")
        st.warning("⚠️ Phát hiện hình thức lừa đảo mới qua mã QR VNeID.")

    elif page == "⚙️ Cài đặt hệ thống":
        st.markdown("## ⚙️ Cài đặt")
        st.text_input("Thay đổi mật khẩu mới")
        st.button("Lưu thay đổi")

# ⚓ 4. Chân trang (Footer)
def footer():
    st.markdown(
        """
        <hr>
        <div style="text-align:center; font-size:14px; color:gray;">
            <a href="#">Báo cáo lỗi hệ thống</a> |
            <a href="#">Chính sách bảo mật</a> |
            <a href="#">Điều khoản sử dụng</a>
            <br><br>
            © Bản quyền thuộc về <b>Trung tâm Dữ liệu Quốc gia về Dân Cư – Bộ Công An</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 🚀 Hàm chính
def app():
    # Kiểm tra đăng nhập
    check_role("officer")

    full_name = st.session_state["full_name"]

    header(full_name)
    page = sidebar()
    main_content(page)
    footer()

if __name__ == "__main__":
    app()
