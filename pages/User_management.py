from services.data_viz_service import load_users, save_users
import uuid
import streamlit as st
import pandas as pd
from services.layout import display_back_button
display_back_button()
st.subheader("Danh sách tài khoản")
users = load_users()

df_users = pd.DataFrame(users)
st.dataframe(df_users[["user_id", "username", "role", "full_name"]])

st.divider()
st.subheader("➕ Thêm người dùng mới")

username = st.text_input("Tên đăng nhập mới")
password = st.text_input("Mật khẩu", type="password")
role = st.selectbox("Vai trò", ["citizen", "officer", "admin"])
full_name = st.text_input("Họ tên")

if st.button("Thêm tài khoản"):
    new_user = {
            "user_id": str(uuid.uuid4())[:8],
            "username": username,
            "password": password,
            "role": role,
            "full_name": full_name
        }
    users.append(new_user)
    save_users(users)
    st.success(f"Đã thêm tài khoản '{username}' ({role}) thành công!")
    st.rerun()