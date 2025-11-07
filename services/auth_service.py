def authenticate_user():
    #xác thực
    pass

def check_permission():
    #kiem tra quyen
    pass

import json
import streamlit as st
from pathlib import Path

DATA_PATH = Path("data/db/users.json")

# Đọc dữ liệu người dùng
def load_users():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        st.error("Không tìm thấy users.json trong thư mục data/")
        return []

# Xác thực tài khoản
def authenticate_user(user_id, password):
    users = load_users()
    for user in users:
        if user["user_id"] == user_id and user["password"] == password:
            return user
    return None

# Sau khi đăng nhập thành công
def login_success(user):
    st.session_state["is_logged_in"] = True
    st.session_state["user_id"] = user["user_id"]
    st.session_state["username"] = user["username"]
    st.session_state["role"] = user["role"]
    st.session_state["full_name"] = user["full_name"]

# Đăng xuất
def logout():
    for key in ["is_logged_in", "user_id", "username", "role", "full_name"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Kiểm tra quyền truy cập theo role
def check_role(required_role):
    if "is_logged_in" not in st.session_state:
        st.error("Bạn chưa đăng nhập!")
        st.stop()
    if st.session_state.get("role") != required_role:
        st.error("Bạn không có quyền truy cập trang này!")
        st.stop()
