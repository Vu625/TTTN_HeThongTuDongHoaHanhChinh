import streamlit as st
from services.auth_service import load_users,authenticate_user,login_success
users = load_users()

# ---------- GIAO DIỆN ----------
st.set_page_config(page_title="Đăng nhập - VNeID", layout="centered")
st.markdown("<h2 style='text-align:center; color:#0056A1;'>🔐 ĐĂNG NHẬP VNeID</h2>", unsafe_allow_html=True)

user_id = st.text_input("🪪 Số định danh cá nhân / CCCD", max_chars=12)
password = st.text_input("🔑 Mật khẩu", type="password")
login_btn = st.button("✅ Đăng nhập")

# ---------- XỬ LÝ ĐĂNG NHẬP ----------
if login_btn:
    if not user_id or not password:
        st.warning("Vui lòng nhập đầy đủ thông tin.")
    else:
        user = authenticate_user(user_id, password)
        if user and password == user["password"]:
            login_success(user)
            st.success("Đăng nhập thành công! Đang chuyển hướng...")

            # Dùng Streamlit switch_page (Streamlit >= 1.25)
            if user["role"] == "citizen":
                st.switch_page("pages/Citizen_Home.py")
            elif user["role"] == "officer":
                st.switch_page("pages/Officer_Home.py")
            elif user["role"] == "admin":
                st.switch_page("pages/Admin_Home.py")
        else:
            st.error("Sai CCCD hoặc mật khẩu.")

st.markdown("---")
st.markdown("[🔄 Quên mật khẩu](#) | [📱 Đăng nhập bằng OTP](#) | [📷 Mã QR](#)")
st.info("⚠️ Không chia sẻ tài khoản hoặc mã OTP cho người khác.")
