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
