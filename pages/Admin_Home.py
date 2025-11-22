import streamlit as st
from services.auth_service import check_role, logout
from services.data_viz_service import get_statistics, load_users, save_users
from services.ocr_service import read_text_from_pdf
from services.layout import check_and_switch
import time
import pandas as pd
import plotly.express as px
import uuid
import os

check_role("admin")

# st.title("📊 Bảng điều khiển quản trị hệ thống")
#
# menu = st.sidebar.radio("Chức năng", ["📈 Dashboard thống kê", "👥 Quản lý người dùng", "⚙️ Cấu hình Chatbot"])
#
# # === DASHBOARD ===
# if menu == "📈 Dashboard thống kê":
#     stats = get_statistics()
#     if not stats:
#         st.info("Chưa có dữ liệu hồ sơ để thống kê.")
#     else:
#         st.subheader("📊 Thống kê tổng quan")
#         col1, col2 = st.columns(2)
#         col1.metric("Tổng số hồ sơ", stats["total"])
#         col2.metric("Số thủ tục", len(stats["by_procedure"]))
#
#         st.divider()
#
#         st.subheader("🔍 Phân bố hồ sơ theo trạng thái")
#         df_status = pd.DataFrame(list(stats["by_status"].items()), columns=["Trạng thái", "Số lượng"])
#         fig1 = px.bar(df_status, x="Trạng thái", y="Số lượng", color="Trạng thái", text_auto=True)
#         st.plotly_chart(fig1, use_container_width=True)
#
#         st.subheader("📂 Thủ tục được sử dụng nhiều nhất")
#         df_proc = pd.DataFrame(list(stats["by_procedure"].items()), columns=["Thủ tục", "Số lượng"])
#         fig2 = px.pie(df_proc, names="Thủ tục", values="Số lượng", title="Tỷ lệ thủ tục")
#         st.plotly_chart(fig2, use_container_width=True)
#
# # === QUẢN LÝ NGƯỜI DÙNG ===
# elif menu == "👥 Quản lý người dùng":
#     st.subheader("Danh sách tài khoản")
#     users = load_users()
#
#     df_users = pd.DataFrame(users)
#     st.dataframe(df_users[["user_id", "username", "role", "full_name"]])
#
#     st.divider()
#     st.subheader("➕ Thêm người dùng mới")
#
#     username = st.text_input("Tên đăng nhập mới")
#     password = st.text_input("Mật khẩu", type="password")
#     role = st.selectbox("Vai trò", ["citizen", "officer", "admin"])
#     full_name = st.text_input("Họ tên")
#
#     if st.button("Thêm tài khoản"):
#         new_user = {
#             "user_id": str(uuid.uuid4())[:8],
#             "username": username,
#             "password": password,
#             "role": role,
#             "full_name": full_name
#         }
#         users.append(new_user)
#         save_users(users)
#         st.success(f"Đã thêm tài khoản '{username}' ({role}) thành công!")
#         st.rerun()
#
# # === CẤU HÌNH HỆ THỐNG ===
# elif menu == "⚙️ Cấu hình Chatbot":
#     # - Bật/tắt cache AI
#     FOLDER_PATH = 'data/db/law_texts'
#     # --- CẤU HÌNH ---
#     if not os.path.exists(FOLDER_PATH):
#         os.makedirs(FOLDER_PATH)
#
#     st.title("📂 Quản lý Tài Liệu (TXT & OCR PDF)")
#
#     # Khởi tạo session state
#     if 'edit_file' not in st.session_state: st.session_state.edit_file = None
#     if 'view_file' not in st.session_state: st.session_state.view_file = None
#
#     # --- PHẦN 1: UPLOAD FILE (TXT HOẶC PDF) ---
#     st.subheader("1. Thêm tài liệu mới")
#     # Cho phép nhận cả txt và pdf
#     uploaded_file = st.file_uploader("Chọn file .txt hoặc .pdf", type=['txt', 'pdf'], label_visibility="collapsed")
#
#     if uploaded_file is not None:
#         file_ext = uploaded_file.name.split('.')[-1].lower()
#
#         # TRƯỜNG HỢP 1: FILE PDF (Cần OCR)
#         if file_ext == 'pdf':
#             # 1. Lưu file PDF tạm thời
#             temp_pdf_path = os.path.join(FOLDER_PATH, uploaded_file.name)
#             with open(temp_pdf_path, "wb") as f:
#                 f.write(uploaded_file.getbuffer())
#
#             # 2. Hiển thị trạng thái đang xử lý
#             with st.spinner('Đang chạy OCR để đọc tài liệu... vui lòng đợi ⏳'):
#                 # Gọi hàm xử lý của bạn
#                 result = read_text_from_pdf(temp_pdf_path)
#
#             # 3. Xử lý kết quả
#             if result["status"] == "SUCCESS":
#                 # Tạo tên file txt tương ứng (ví dụ: tailieu.pdf -> tailieu.txt)
#                 txt_filename = uploaded_file.name.rsplit('.', 1)[0] + ".txt"
#                 txt_save_path = os.path.join(FOLDER_PATH, txt_filename)
#
#                 # Nối nội dung các trang lại với nhau
#                 full_content = "\n\n".join(result["text_by_page"])
#
#                 # Lưu file .txt
#                 with open(txt_save_path, "w", encoding="utf-8") as f:
#                     f.write(full_content)
#
#                 # Xóa file PDF tạm đi (nếu bạn không muốn giữ lại)
#                 os.remove(temp_pdf_path)
#
#                 st.success(f"✅ Đã chuyển đổi PDF thành công! ({result['pages_count']} trang)")
#                 time.sleep(1)
#                 st.rerun()
#
#             else:
#                 st.error(result["message"])
#                 # Xóa file lỗi nếu cần
#                 if os.path.exists(temp_pdf_path):
#                     os.remove(temp_pdf_path)
#
#         # TRƯỜNG HỢP 2: FILE TXT (Lưu trực tiếp)
#         else:
#             save_path = os.path.join(FOLDER_PATH, uploaded_file.name)
#             with open(save_path, "wb") as f:
#                 f.write(uploaded_file.getbuffer())
#             st.success(f"✅ Đã thêm file text: {uploaded_file.name}")
#             time.sleep(0.5)
#             st.rerun()
#
#
#     st.markdown("---")
#
#     # --- PHẦN 2: DANH SÁCH & CHỨC NĂNG ---
#     st.subheader("2. Danh sách tài liệu")
#
#     files = [f for f in os.listdir(FOLDER_PATH) if f.endswith('.txt')]
#
#     if not files:
#         st.info("Chưa có file nào.")
#     else:
#         for file_name in files:
#             file_path = os.path.join(FOLDER_PATH, file_name)
#
#             # Chia cột: Tên (5 phần) | Xem (1.5 phần) | Sửa (1.5 phần) | Xóa (2 phần)
#             col1, col2, col3, col4 = st.columns([5, 1.5, 1.5, 2])
#
#             with col1:
#                 st.text(f"📄 {file_name}")
#
#             with col2:
#                 # NÚT XEM (Toggle: Bấm để hiện/ẩn)
#                 if st.button("Xem", key=f"view_{file_name}"):
#                     # Nếu đang xem file này thì đóng lại (gán None), chưa thì mở ra
#                     if st.session_state.get('view_file') == file_name:
#                         st.session_state.view_file = None
#                     else:
#                         st.session_state.view_file = file_name
#                         st.session_state.edit_file = None  # Tắt chế độ sửa nếu đang mở
#
#             with col3:
#                 # NÚT SỬA
#                 if st.button("Sửa", key=f"edit_{file_name}"):
#                     # Nếu đang sửa file này thì đóng lại, chưa thì mở ra
#                     if st.session_state.edit_file == file_name:
#                         st.session_state.edit_file = None
#                     else:
#                         st.session_state.edit_file = file_name
#                         st.session_state.view_file = None  # Tắt chế độ xem nếu đang mở
#
#             with col4:
#                 # NÚT XÓA
#                 if st.button("Xóa ❌", key=f"del_{file_name}"):
#                     os.remove(file_path)
#                     # Reset lại trạng thái để tránh lỗi
#                     if st.session_state.edit_file == file_name: st.session_state.edit_file = None
#                     if st.session_state.get('view_file') == file_name: st.session_state.view_file = None
#                     st.toast(f"Đã xóa {file_name}")
#                     import time
#
#                     time.sleep(0.5)
#                     st.rerun()
#
#             # --- KHU VỰC HIỂN THỊ NỘI DUNG (XEM HOẶC SỬA) ---
#
#             # 1. Logic hiển thị khung XEM
#             if st.session_state.get('view_file') == file_name:
#                 with open(file_path, "r", encoding="utf-8") as f:
#                     content = f.read()
#                 st.info(f"Nội dung file: {file_name}")
#                 st.code(content, language='text')  # Dùng st.code nhìn cho đẹp
#
#             # 2. Logic hiển thị khung SỬA
#             if st.session_state.edit_file == file_name:
#                 st.warning(f"✏️ Đang sửa: {file_name}")
#
#                 # Đọc nội dung hiện tại để đưa vào ô nhập liệu
#                 with open(file_path, "r", encoding="utf-8") as f:
#                     current_content = f.read()
#
#                 # Tạo Form để khi bấm Lưu mới submit
#                 with st.form(key=f"form_{file_name}"):
#                     new_content = st.text_area("Nội dung:", value=current_content, height=200)
#
#                     # Chia nút Lưu và Hủy
#                     c1, c2 = st.columns([1, 5])
#                     with c1:
#                         submit_save = st.form_submit_button("💾 Lưu")
#
#                     if submit_save:
#                         # Ghi đè nội dung mới vào file
#                         with open(file_path, "w", encoding="utf-8") as f:
#                             f.write(new_content)
#
#                         st.success("Đã cập nhật thành công!")
#                         st.session_state.edit_file = None  # Tắt chế độ sửa sau khi lưu
#                         st.rerun()  # Load lại trang

def header(username):
    st.markdown(
        """
        <style>
        .header {
            background-color: #880E4F; /* đỏ tím sang trọng */
            padding: 10px 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: white;
            border-bottom: 4px solid #F48FB1;
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
            color: #880E4F;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
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
        """,
        unsafe_allow_html=True,
    )
    col_nav, col_login = st.columns([9, 1])

    # --- CÁC NÚT ĐIỀU HƯỚNG ---
    with col_nav:
        st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)
        nav_cols = st.columns([1, 1, 1, 1, 1.3, 1])

        check_and_switch(nav_cols[0], "Trang chủ", "app.py", "btn_home")
        check_and_switch(nav_cols[1], "Dashboard", "Admin_Dashboard.py", "btn_intro")
        check_and_switch(nav_cols[2], "Quản Lí Người Dùng", "User_management.py", "btn_news")
        check_and_switch(nav_cols[3], "Cài Đặt ChatBot", "Setting_Chatbot.py", "btn_guide")
        check_and_switch(nav_cols[4], "Văn bản pháp lý", "app_Legal_documents.py", "btn_legal")
        check_and_switch(nav_cols[5], "Hỏi đáp", "AI_Assistant.py", "btn_ai")

        st.markdown('</div>', unsafe_allow_html=True)

    # --- NÚT ĐĂNG XUẤT ---
    with col_login:
        # st.markdown('<div id="login-btn-wrapper">', unsafe_allow_html=True)
        if st.button("Đăng xuất", key="login_btn"):
            logout()
        # st.markdown('</div>', unsafe_allow_html=True)

# 💬 3. Nội dung chính
def main_content(page):
    full_name = st.session_state["full_name"]

    if page == "🏠 Trang chủ":
        st.markdown(f"<h2>👋 Xin chào, {full_name}</h2>", unsafe_allow_html=True)
        st.info("Chào mừng bạn đến với bảng điều khiển quản trị hệ thống quốc gia.")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Người dùng hoạt động", "1,024")
        with col2:
            st.metric("Hồ sơ chờ duyệt", "58")
        with col3:
            st.metric("Lượt truy cập hôm nay", "12,340")

    elif page == "👥 Quản lý người dùng":
        st.markdown("## 👥 Quản lý người dùng")
        st.write("Thêm, xóa hoặc chỉnh sửa tài khoản công dân / cán bộ / admin.")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Tìm kiếm người dùng (tên hoặc CCCD)")
            st.button("🔍 Tìm kiếm")
        with col2:
            st.selectbox("Vai trò", ["citizen", "officer", "admin"])
        st.table([
            {"CCCD": "572957398571", "Họ tên": "Nguyễn Văn A", "Vai trò": "citizen"},
            {"CCCD": "495939493939", "Họ tên": "Trần Thị B", "Vai trò": "officer"},
        ])
        st.button("➕ Thêm tài khoản mới")

    elif page == "🗃️ Quản lý nội dung":
        st.markdown("## 🗃️ Quản lý nội dung")
        st.write("Duyệt, chỉnh sửa hoặc xóa bài viết, bình luận, hình ảnh, video...")
        st.checkbox("Ẩn nội dung vi phạm tự động", value=True)
        st.button("📜 Duyệt nội dung mới")

    elif page == "💼 Quản lý hệ thống":
        st.markdown("## 💼 Cấu hình hệ thống")
        st.text_input("Tên hệ thống", "CSDL Quốc gia về Dân cư")
        st.text_input("Email quản trị", "admin@phuong.gov")
        st.text_input("Tên miền (domain)", "https://dancu.gov.vn")
        st.button("💾 Lưu cấu hình")

    elif page == "🔒 Bảo mật & truy cập":
        st.markdown("## 🔒 Bảo mật & kiểm soát truy cập")
        st.checkbox("Bật xác thực hai lớp (2FA)", value=True)
        st.checkbox("Ghi nhật ký truy cập", value=True)
        st.button("🔍 Xem nhật ký hệ thống")

    elif page == "📊 Thống kê & báo cáo":
        st.markdown("## 📊 Thống kê hệ thống")
        st.metric("Lượt truy cập tháng này", "432,122")
        st.metric("Người dùng mới", "+2,543")
        st.line_chart({"Truy cập": [30000, 42000, 37000, 39000, 45000]})
        st.button("📤 Xuất báo cáo CSV")

    elif page == "🛍️ Quản lý thương mại (tùy chọn)":
        st.markdown("## 🛍️ Quản lý thương mại điện tử")
        st.warning("Chức năng này chỉ khả dụng khi hệ thống kích hoạt module thương mại.")
        st.button("Bật module thương mại")

    elif page == "🎨 Tùy biến & giao diện":
        st.markdown("## 🎨 Tùy biến giao diện")
        st.color_picker("Chọn màu chủ đạo", "#880E4F")
        st.selectbox("Giao diện", ["Sáng", "Tối", "Tự động"])
        st.button("💾 Lưu thay đổi")

    elif page == "🔁 Phân quyền & vai trò":
        st.markdown("## 🔁 Quản lý vai trò và quyền hạn")
        st.selectbox("Nhóm quyền", ["Admin", "Officer", "Citizen", "Moderator"])
        st.checkbox("Truy cập quản trị")
        st.checkbox("Chỉnh sửa nội dung")
        st.checkbox("Xem thống kê")
        st.button("✅ Cập nhật quyền")

    # elif page == "⚙️ Cài đặt chung":
    #     st.markdown("## ⚙️ Cài đặt tài khoản")
    #     st.text_input("Tên hiển thị", value=full_name)
    #     st.text_input("Email", value=user.get("email", ""))
    #     st.text_input("Mật khẩu mới", type="password")
    #     st.button("💾 Lưu thay đổi")

# ⚓ 4. Chân trang (Footer)
def footer():
    st.markdown(
        """
        <hr>
        <div style="text-align:center; font-size:14px; color:gray;">
            <a href="#">Trung tâm hỗ trợ kỹ thuật</a> |
            <a href="#">Chính sách bảo mật</a> |
            <a href="#">Điều khoản sử dụng</a>
            <br><br>
            © Bản quyền thuộc về <b>Trung tâm Dữ liệu Quốc Gia về Dân Cư – Bộ Công An</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 🚀 Hàm chính
def app():
    # if "current_user" not in st.session_state:
    #     st.warning("⚠️ Bạn chưa đăng nhập. Vui lòng quay lại trang đăng nhập.")
    #     st.stop()

    # user = st.session_state["current_user"]
    full_name = st.session_state["full_name"]

    header(full_name)
    page = "🏠 Trang chủ"
    main_content(page)
    footer()

# Khi chạy độc lập
if __name__ == "__main__":
    app()