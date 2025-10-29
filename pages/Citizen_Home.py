import streamlit as st
from services.auth_service import check_role, logout

check_role("citizen")

st.title("🏠 Trang chủ Công dân")

st.write("Chức năng khả dụng:")
st.markdown("""
- 📝 Nộp hồ sơ
- 🔍 Tra cứu tiến độ
- 💬 Chat hỗ trợ AI
- 👤 Hồ sơ cá nhân
""")

if st.sidebar.button("Đăng xuất"):
    logout()
