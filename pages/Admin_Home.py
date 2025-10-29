import streamlit as st
from services.auth_service import check_role, logout

check_role("admin")

st.title("📊 Trang chủ Quản trị")

st.write("Chức năng khả dụng:")
st.markdown("""
- 👥 Quản lý người dùng
- 📈 Dashboard thống kê
- 🔧 Cấu hình hệ thống
""")

if st.sidebar.button("Đăng xuất"):
    logout()
