import streamlit as st
#from utils.auth import authenticate_user, login_success, logout
from services.auth_service import authenticate_user,login_success,logout
# Cấu hình giao diện cơ bản
st.set_page_config(page_title="Hệ thống Hành chính AI", page_icon="🤖")


def show_login_page():
    st.title("🔐 Đăng nhập hệ thống")

    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")

    if st.button("Đăng nhập"):
        user = authenticate_user(username, password)
        if user:
            login_success(user)
            st.success("Đăng nhập thành công!")
            st.rerun()
        else:
            st.error("Sai tài khoản hoặc mật khẩu!")


def show_logged_in():
    st.sidebar.write(f"👤 Xin chào: **{st.session_state['full_name']}**")
    if st.sidebar.button("Đăng xuất"):
        logout()

    role = st.session_state.get("role")

    if role == "citizen":
        st.switch_page("pages/Citizen_Home.py")
    elif role == "officer":
        st.switch_page("pages/Officer_Home.py")
    elif role == "admin":
        st.switch_page("pages/Admin_Home.py")
    else:
        st.error("Không xác định vai trò người dùng!")


# Luồng chính
if "is_logged_in" not in st.session_state:
    show_login_page()
else:
    show_logged_in()


