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
                    <img src="https://play-lh.googleusercontent.com/k2J4mfmUj040c4dKuVwAg4CwR_4k_RRTO_Zb3a8dMGRynKTaUjek3P_i_MKjmFPG87uK=w480-h960-rw">
                <div>
                    <div style="font-weight:bold; font-size:18px;">BỘ CÔNG AN</div>
                    <div style="font-size:14px;">TRUNG TÂM DỮ LIỆU QUỐC GIA VỀ DÂN CƯ</div>
                </div>
            </div>
            <div class="header-center">
                <img src="https://icons.veryicon.com/png/o/miscellaneous/yuanql/icon-admin.png">
            </div>
            <div class="header-right">
                <span>🔔</span>
                <span>{username}</span>
                <div class="avatar">🛠</div>
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
        check_and_switch(nav_cols[4], "Thay đổi mật khẩu", "Change_Password.py", "btn_legal")
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