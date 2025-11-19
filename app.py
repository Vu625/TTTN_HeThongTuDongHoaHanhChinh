import streamlit as st
import os

current_file_name = os.path.basename(__file__)

# --- CSS CẢI TIẾN ---
st.markdown(
    """
    <style>
        /* Header chính */
        .header {
            background: linear-gradient(135deg, #0055A5 0%, #003d7a 100%);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 0;
        }

        /* Container menu */
        #custom-menu-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(180deg, #E6F2FF 0%, #f0f7ff 100%);
            padding: 0;
            margin-top: -16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            border-bottom: 2px solid #0055A5;
        }

        /* Container các nút điều hướng */
        .nav-buttons {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 8px 20px;
            flex: 1;
        }

        /* Ẩn các thành phần không cần thiết */
        .st-emotion-cache-nahz7x, 
        .st-emotion-cache-1629p8f,
        .st-emotion-cache-1gf9f20,
        .st-emotion-cache-1wbts04 {
            padding: 0 !important;
            margin: 0 !important;
        }

        /* CSS chung cho tất cả nút điều hướng */
        div.stButton > button {
            background-color: transparent !important;
            color: #333333;
            border: none;
            padding: 10px 18px !important;
            font-weight: 500;
            font-size: 15px;
            white-space: nowrap;
            height: 45px;
            border-radius: 6px;
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
        }

        /* Hiệu ứng hover cho nút điều hướng */
        div.stButton > button:hover:not(:disabled) {
            color: #E60000 !important;
            background-color: rgba(230, 0, 0, 0.08) !important;
            border-bottom: 3px solid #E60000;
            transform: translateY(-2px);
        }

        /* Nút đang active (disabled) */
        div.stButton > button:disabled {
            color: #E60000 !important;
            background-color: rgba(230, 0, 0, 0.12) !important;
            border-bottom: 3px solid #E60000;
            font-weight: 600;
            cursor: default;
        }

        /* Container nút đăng nhập */
        #login-btn-wrapper {
            padding: 8px 20px;
            display: flex;
            align-items: center;
        }

        /* CSS riêng cho nút Đăng nhập */
        #login-btn-wrapper button {
            color: #E60000 !important;
            background: white !important;
            border: 2px solid #E60000 !important;
            border-radius: 20px !important;
            padding: 8px 24px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            height: auto !important;
            box-shadow: 0 2px 4px rgba(230, 0, 0, 0.2);
            transition: all 0.3s ease;
        }

        #login-btn-wrapper button:hover {
            background: linear-gradient(135deg, #E60000 0%, #cc0000 100%) !important;
            color: white !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(230, 0, 0, 0.3);
        }

        /* Divider */
        hr {
            margin-top: 0 !important;
            margin-bottom: 20px !important;
            border-color: #e0e0e0 !important;
        }
    </style>
    <div class="header">
        🌐 HỆ THỐNG ĐỊNH DANH VÀ XÁC THỰC ĐIỆN TỬ QUỐC GIA (VNeID)
    </div>
    """,
    unsafe_allow_html=True
)

# --- BẮT ĐẦU CONTAINER MENU ---
st.markdown('<div id="custom-menu-container">', unsafe_allow_html=True)

# Tạo 2 cột chính: menu điều hướng và nút đăng nhập
col_nav, col_login = st.columns([9, 1])


# Hàm kiểm tra và chuyển trang
def check_and_switch(col, button_text, page_file, key):
    is_current_page = (current_file_name == page_file)
    with col:
        if st.button(button_text, key=key, disabled=is_current_page):
            if page_file == "app.py":
                st.switch_page(page_file)
            else:
                st.switch_page(f"pages/{page_file}")


# --- CÁC NÚT ĐIỀU HƯỚNG ---
with col_nav:
    st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)
    nav_cols = st.columns([1, 1, 1, 1, 1.3, 1])

    check_and_switch(nav_cols[0], "Trang chủ", "app.py", "btn_home")
    check_and_switch(nav_cols[1], "Giới thiệu", "app_Introduce.py", "btn_intro")
    check_and_switch(nav_cols[2], "Tin tức", "app_news.py", "btn_news")
    check_and_switch(nav_cols[3], "Hướng dẫn", "Huong_dan.py", "btn_guide")
    check_and_switch(nav_cols[4], "Văn bản pháp lý", "app_Legal_documents.py", "btn_legal")
    check_and_switch(nav_cols[5], "Hỏi đáp", "AI_Assistant.py", "btn_ai")

    st.markdown('</div>', unsafe_allow_html=True)

# --- NÚT ĐĂNG NHẬP ---
with col_login:
    st.markdown('<div id="login-btn-wrapper">', unsafe_allow_html=True)
    if st.button("🔴 Đăng nhập", key="login_btn"):
        st.switch_page("pages/Login_page.py")
    st.markdown('</div>', unsafe_allow_html=True)

# --- KẾT THÚC CONTAINER MENU ---
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ------------------ HERO SECTION ------------------
st.image(
    "https://lamdong.gov.vn/sites/chuyendoiso/tin-tong-hop/SiteAssets/SitePages/ca-1660876159706.jpg",
    use_container_width=True,
)
st.markdown("""
### 🔒 ĐỊNH DANH ĐIỆN TỬ QUỐC GIA – KẾT NỐI AN TOÀN, THUẬN TIỆN
Ứng dụng giúp người dân thực hiện các dịch vụ công, xác thực danh tính, và tích hợp giấy tờ cá nhân trên nền tảng số.
""")

st.link_button("📲 Tải ứng dụng VNeID", "https://vneid.gov.vn/")

# ------------------ GIỚI THIỆU ------------------
with st.container():
    st.divider()
    st.subheader("📘 Giới thiệu hệ thống")
    st.write("""
    VNeID là hệ thống định danh và xác thực điện tử do **Bộ Công an** triển khai, 
    nhằm mục tiêu xây dựng nền tảng **chính phủ số và công dân số** tại Việt Nam.

    **Tiện ích chính:**
    - Xác thực danh tính công dân nhanh chóng, an toàn.
    - Tích hợp giấy tờ cá nhân (CMND, GPLX, BHYT, CCCD gắn chip,...).
    - Hỗ trợ thực hiện dịch vụ công trực tuyến toàn quốc.
    """)

# ------------------ TÍNH NĂNG ------------------
with st.container():
    st.divider()
    st.subheader("⚙️ Tiện ích nổi bật")
    cols = st.columns(5)
    features = [
        ("🪪", "Xác thực danh tính"),
        ("🏠", "Khai báo cư trú"),
        ("📄", "Tích hợp giấy tờ"),
        ("💼", "Dịch vụ công"),
        ("💰", "Thanh toán điện tử")
    ]
    for col, (icon, name) in zip(cols, features):
        with col:
            st.markdown(f"<h1 style='text-align:center'>{icon}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center'><b>{name}</b></p>", unsafe_allow_html=True)

# ------------------ FOOTER ------------------
st.divider()
st.markdown(
    """
    <div style="text-align:center; color:gray; font-size:14px;">
        <p>Cục C06 - Bộ Công an Việt Nam</p>
        <p>Địa chỉ: 47 Phạm Văn Đồng, Hà Nội | Điện thoại: 069.234.2590 | Email: hotro@vneid.gov.vn</p>
        <p>© 2025 Bản quyền thuộc Bộ Công an Việt Nam</p>
    </div>
    """,
    unsafe_allow_html=True
)
