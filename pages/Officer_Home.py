import streamlit as st
from services.auth_service import check_role, logout

check_role("officer")

st.title("🛠 Trang chủ Cán bộ xử lý")

st.write("Chức năng khả dụng:")
st.markdown("""
- 📥 Nhận & xử lý hồ sơ
- 📚 Quản lý tài liệu pháp luật
- 💬 Hỗ trợ công dân
""")

if st.sidebar.button("Đăng xuất"):
    logout()
