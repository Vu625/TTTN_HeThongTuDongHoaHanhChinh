import streamlit as st
from services.auth_service import logout
def load_common_layout():
    """Hiển thị layout (sidebar) chung cho tất cả các trang."""
    with st.sidebar:
        # Logo hoặc biểu tượng
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=80)
        st.markdown("### 🇻🇳 Hệ thống VNeID")

        # Thông tin người dùng (nếu đã đăng nhập)
        username = st.session_state.get("username", "Khách")
        role = st.session_state.get("role", "Chưa xác định")

        st.markdown(f"👤 **{username}**")
        st.caption(f"Vai trò: {role}")
        st.markdown("---")

        # Menu điều hướng chung
        selected = st.radio(
            "📂 Danh mục",
            ["🏠 Trang chủ", "📰 Nộp Hồ Sơ", "🏢 Tổ chức", "⚙️ Cài đặt"],
            key="menu_sidebar"
        )

        st.markdown("---")
        if st.button("🚪 Đăng xuất"):
            logout()
            # st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("© 2025 VNeID Citizen System")

        # Trả về lựa chọn
        return selected


def display_back_button():
    """
    Hiển thị nút "Quay Lại" bằng st.page_link, trỏ đến Trang Chủ của người dùng
    (Citizen Home hoặc Admin Home) dựa trên Session State.
    """

    # 1. Xác định trang chủ dựa trên vai trò (Role) đã lưu trong session state
    role = st.session_state.get("role")

    if role == "citizen":
        home_page_path = "pages/Citizen_Home.py"
        label = "⬅️ Quay lại Trang Chủ Công Dân"
    elif role == "admin":
        # Giả sử admin muốn quay về Dashboard
        home_page_path = "pages/Admin_Dashboard.py"
        label = "⬅️ Quay lại Bảng Điều Khiển Admin"
    elif role == "officer":
        home_page_path = "pages/Officer_Dashboard.py"
        label = "⬅️ Quay lại Trang Cán bộ"
    else:
        # Mặc định hoặc khi chưa đăng nhập
        # app.py thường là trang đăng nhập hoặc trang giới thiệu
        home_page_path = "app.py"
        label = "⬅️ Quay lại Trang Đăng Nhập"

    # 2. Hiển thị nút page_link
    st.markdown("---")  # Thêm một đường kẻ để tách biệt nút
    st.page_link(
        home_page_path,
        label=label,
        icon="🏠"
    )