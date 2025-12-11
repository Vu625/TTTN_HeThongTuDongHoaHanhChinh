import streamlit as st
from services.auth_service import load_users,authenticate_user,login_success
users = load_users()

# ---------- GIAO DIỆN ----------
st.subheader("📝 Đăng nhập tài khoản")
col1, col2 = st.columns(2)

with col1:
    login_btn = st.button("✅ Đăng nhập", type="primary", use_container_width=True)

with col2:
    # Nút này sẽ chuyển hướng sang file Register.py bạn vừa sửa
    register_btn = st.button("📝 Đăng ký tài khoản", use_container_width=True)

if register_btn:
    st.switch_page("pages/Register.py")

with st.form("login_form", clear_on_submit=True):
    user_id = st.text_input("💳 Số định danh cá nhân / CCCD", max_chars=12)
    password = st.text_input("🔑 Mật khẩu", type="password")
    # login_btn = st.button("✅ Đăng nhập")
    st.divider()
    submitted = st.form_submit_button("✅ Đăng nhập", type="primary", use_container_width=True)
    # ---------- XỬ LÝ ĐĂNG NHẬP ----------
    if submitted:
        if not user_id or not password:
            st.warning("Vui lòng nhập đầy đủ thông tin.")
        else:
            user = authenticate_user(user_id, password)
            if user:
                login_success(user)
                st.success("Đăng nhập thành công! Đang chuyển hướng...")
                if user["role"] == "citizen":
                    st.switch_page("pages/Citizen_Home.py")
                elif user["role"] == "officer":
                    st.switch_page("pages/Officer_Home.py")
                elif user["role"] == "admin":
                    st.switch_page("pages/Admin_Home.py")
            else:
                st.error("Sai CCCD hoặc mật khẩu.")

st.markdown("---")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    # Nút chuyển trang Quên mật khẩu
    if st.button("🔄 Quên mật khẩu", use_container_width=True):
        try:
            st.switch_page("pages/ForgotPassword.py")
        except Exception:
            st.error("Chưa tìm thấy file pages/ForgotPassword.py")

with col_f2:
    # Nút OTP (Chưa phát triển)
    if st.button("📱 Đăng nhập OTP", use_container_width=True):
        st.info("Chức năng đang phát triển")

with col_f3:
    # Nút QR (Chưa phát triển)
    if st.button("📷 Quét mã QR", use_container_width=True):
        st.info("Chức năng đang phát triển")

# Dòng cảnh báo cuối cùng
st.info("⚠️ Không chia sẻ tài khoản hoặc mã OTP cho người khác.")
