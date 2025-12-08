import streamlit as st
import time
from services.auth_service import load_users, save_users, hash_password

# --- GIAO DIỆN FORM ĐĂNG KÝ ---
st.subheader("📝 Đăng ký tài khoản Công dân")

with st.form("register_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        # User ID và Username
        user_id = st.text_input("Số định danh (CCCD)", key="reg_user_id")
        username = st.text_input("Tên đăng nhập mong muốn", key="reg_username")

    with col2:
        # Họ tên và Mật khẩu
        full_name = st.text_input("Họ và Tên", key="reg_full_name")
        password = st.text_input("Mật khẩu", type="password", key="reg_password")

    # Email để riêng một dòng (hoặc đưa lên col2 tùy bạn)
    email = st.text_input("Email (Gmail)", key="reg_email")

    st.markdown("---")
    submitted = st.form_submit_button("✅ Xác nhận đăng ký", type="primary", use_container_width=True)

    if submitted:
        # 1. Load danh sách cũ
        users = load_users()

        # 2. Kiểm tra nhập thiếu
        if not (user_id and username and password and full_name):
            st.warning("Vui lòng điền đầy đủ thông tin bắt buộc!")

        # 3. Kiểm tra trùng lặp (ID và Username)
        elif any(u.get("user_id") == user_id for u in users):
            st.error(f"⚠️ Số định danh '{user_id}' đã tồn tại trong hệ thống!")
        elif any(u.get("username") == username for u in users):
            st.error(f"⚠️ Tên đăng nhập '{username}' đã có người sử dụng!")

        # 4. Tạo và Lưu tài khoản
        else:
            new_user = {
                "user_id": user_id,
                "username": username,
                "password": hash_password(password),  # Mã hóa password
                "full_name": full_name,
                "email": email,
                "role": "citizen"  # <--- MẶC ĐỊNH LÀ CITIZEN
            }

            users.append(new_user)
            save_users(users)

            st.success(f"🎉 Đăng ký thành công! Chào mừng công dân {full_name}.")
            time.sleep(1.5)
            # Chuyển hướng về trang đăng nhập
            st.switch_page("pages/Login_page.py")

# Nút quay lại thủ công nếu không muốn đăng ký
if st.button("⬅️ Quay lại Đăng nhập"):
    st.switch_page("pages/Login_page.py")