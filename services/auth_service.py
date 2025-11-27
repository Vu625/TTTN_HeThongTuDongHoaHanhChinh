def authenticate_user():
    #xác thực
    pass

def check_permission():
    #kiem tra quyen
    pass
import bcrypt
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

def save_users(users):
    try:
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Lỗi khi lưu dữ liệu người dùng: {e}")

# Xác thực tài khoản
# def authenticate_user(user_id, password):
#     users = load_users()
#     for user in users:
#         if user["user_id"] == user_id and user["password"] == password:
#             return user
#     return None

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

def check_role(*required_roles):
    # 1. KIỂM TRA ĐĂNG NHẬP
    if "is_logged_in" not in st.session_state or not st.session_state.get("is_logged_in"):
        st.error("Bạn chưa đăng nhập!")
        if st.button("Đăng Nhập Ngay!"):
            st.switch_page("pages/Login_page.py")
        st.stop()
    # Lấy vai trò hiện tại của người dùng
    user_role = st.session_state.get("role")
    if user_role not in required_roles:
        st.error("Bạn không có quyền truy cập trang này!")
        if st.button("Đăng Nhập Lại?"):
            st.switch_page("pages/Login_page.py")
        st.stop()

def hash_password(password):
    """Băm mật khẩu bằng bcrypt."""
    # Salt được tự động tạo và lưu trong chuỗi băm
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def check_password(password, hashed_password):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

#--- Hàm xác thực tài khoản---
def authenticate_user(user_id, password):
    users = load_users()
    for user in users:
        if user["user_id"] == user_id:
            if check_password(password, user["password"]):
                return user
    return None

# --- Hàm thay đổi mật khẩu (MỚI) ---
def update_password(user_id, new_password):
    users = load_users()
    for user in users:
        if user["user_id"] == user_id:
            # Băm mật khẩu mới trước khi lưu
            user["password"] = hash_password(new_password)
            save_users(users)
            return True
    return False