from services.auth_service import check_role, logout
from services.layout import check_and_switch
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
            width: 50px;
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
                    <img src="https://play-lh.googleusercontent.com/k2J4mfmUj040c4dKuVwAg4CwR_4k_RRTO_Zb3a8dMGRynKTaUjek3P_i_MKjmFPG87uK=w480-h960-rw">
                <div>
                    <div style="font-weight:bold; font-size:18px;">BỘ CÔNG AN</div>
                    <div style="font-size:14px;">TRUNG TÂM DỮ LIỆU QUỐC GIA VỀ DÂN CƯ</div>
                </div>
            </div>
            <div class="header-center">
                <img src="https://icon-library.com/images/staff-icon/staff-icon-14.jpg">
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
        check_and_switch(nav_cols[1], "Duyệt Hồ Sơ", "Handle_Application.py", "btn_intro")
        check_and_switch(nav_cols[2], "Lịch Sử Duyệt", "History_Handle.py", "btn_news")
        check_and_switch(nav_cols[3], "Cài Đặt Chatbot", "Setting_Chatbot.py", "btn_guide")
        check_and_switch(nav_cols[4], "Thay đổi mật khẩu", "Change_Password.py", "btn_legal")
        check_and_switch(nav_cols[5], "Hỏi đáp", "AI_Assistant.py", "btn_ai")

        st.markdown('</div>', unsafe_allow_html=True)

    # --- NÚT ĐĂNG XUẤT ---
    with col_login:
        # st.markdown('<div id="login-btn-wrapper">', unsafe_allow_html=True)
        if st.button("Đăng xuất", key="login_btn"):
            logout()
        # st.markdown('</div>', unsafe_allow_html=True)

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
        st.markdown(f"<h2>👋 Xin chào Cán Bộ {full_name}</h2>", unsafe_allow_html=True)
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
