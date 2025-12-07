import streamlit as st
import json
import os
import bcrypt  # Import thư viện mã hóa

# --- CẤU HÌNH ĐƯỜNG DẪN ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
USER_FILE = os.path.join(project_root, 'data', 'db', 'users.json')


def load_users():
    if not os.path.exists(USER_FILE):
        return []
    try:
        with open(USER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []


def save_user(new_user_data):
    users = load_users()

    # Kiểm tra trùng ID
    for user in users:
        if user.get('user_id') == new_user_data['user_id']:
            return False, "Số định danh này đã tồn tại!"

    users.append(new_user_data)
    os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)

    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

    return True, "Đăng ký thành công!"


# --- GIAO DIỆN ---
st.set_page_config(page_title="Đăng Ký", page_icon="📝")
st.markdown("<h2 style='text-align:center; color:#E03C31;'>📝 ĐĂNG KÝ CÔNG DÂN</h2>", unsafe_allow_html=True)

with st.form("register_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Họ và Tên")
        user_id = st.text_input("Số định danh (CCCD)")
    with col2:
        email = st.text_input("Gmail")
        password = st.text_input("Mật khẩu", type="password")

    st.markdown("---")
    submitted = st.form_submit_button("Xác nhận đăng ký", type="primary", use_container_width=True)

# --- XỬ LÝ LOGIC ---
if submitted:
    if not (full_name and user_id and email and password):
        st.warning("Vui lòng nhập đầy đủ thông tin!")
    else:
        # 1. Mã hóa mật khẩu
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password_str = hashed_bytes.decode('utf-8')  # Chuyển bytes thành string để lưu JSON

        # 2. Tạo data đúng cấu trúc user.json của bạn
        new_user = {
            "user_id": user_id,
            "username": user_id,  # Tự động lấy user_id làm username (hoặc bạn có thể thêm input riêng)
            "password": hashed_password_str,  # Lưu mật khẩu đã mã hóa
            "role": "citizen",
            "full_name": full_name,
            "email": email
        }

        success, message = save_user(new_user)

        if success:
            st.success(message)
            if st.button("⬅️ Quay về Đăng nhập"):
                st.switch_page("pages/Login_page.py")
        else:
            st.error(message)

# Nút quay về
st.markdown("---")
if st.button("Đã có tài khoản? Đăng nhập"):
    st.switch_page("pages/Login_page.py")