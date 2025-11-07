import streamlit as st

# ------------------ CẤU HÌNH TRANG ------------------
st.set_page_config(
    page_title="Hệ thống định danh và xác thực điện tử - Mô phỏng VNeID",
    page_icon="🌐",
    layout="wide"
)

# ------------------ HEADER ------------------
st.markdown(
    """
    <style>
        .header {
            background-color: #0055A5;
            color: white;
            padding: 15px;
            text-align: center;
            font-size: 26px;
            font-weight: bold;
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
    <div class="header">
        🌐 HỆ THỐNG ĐỊNH DANH VÀ XÁC THỰC ĐIỆN TỬ QUỐC GIA (VNeID)
    </div>
    <div class="menu">
        <a href="/">Trang chủ</a>
        <a href="/Giới_thiệu">Giới thiệu</a>
        <a href="/Tin_tức">Tin tức</a>
        <a href="/Hướng_dẫn">Hướng dẫn</a>
        <a href="/Văn_bản_pháp_lý">Văn bản pháp lý</a>
        <a href="/Hỏi_đáp">Hỏi đáp</a>
        <a href="/Login_page" style="float:right; color:red;">Đăng nhập</a>
    </div>
    """,
    unsafe_allow_html=True
)


# ------------------ HERO SECTION ------------------
st.image(
    "https://vneid.gov.vn/images/banner-home.jpg",
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
