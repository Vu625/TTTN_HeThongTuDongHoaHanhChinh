import streamlit as st
from services.auth_service import check_role, logout
from services.data_viz_service import get_statistics, load_users, save_users
import pandas as pd
import plotly.express as px
import uuid

check_role("admin")

st.title("📊 Bảng điều khiển quản trị hệ thống")

menu = st.sidebar.radio("Chức năng", ["📈 Dashboard thống kê", "👥 Quản lý người dùng", "⚙️ Cấu hình hệ thống"])

# === DASHBOARD ===
if menu == "📈 Dashboard thống kê":
    stats = get_statistics()
    if not stats:
        st.info("Chưa có dữ liệu hồ sơ để thống kê.")
    else:
        st.subheader("📊 Thống kê tổng quan")
        col1, col2 = st.columns(2)
        col1.metric("Tổng số hồ sơ", stats["total"])
        col2.metric("Số thủ tục", len(stats["by_procedure"]))

        st.divider()

        st.subheader("🔍 Phân bố hồ sơ theo trạng thái")
        df_status = pd.DataFrame(list(stats["by_status"].items()), columns=["Trạng thái", "Số lượng"])
        fig1 = px.bar(df_status, x="Trạng thái", y="Số lượng", color="Trạng thái", text_auto=True)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📂 Thủ tục được sử dụng nhiều nhất")
        df_proc = pd.DataFrame(list(stats["by_procedure"].items()), columns=["Thủ tục", "Số lượng"])
        fig2 = px.pie(df_proc, names="Thủ tục", values="Số lượng", title="Tỷ lệ thủ tục")
        st.plotly_chart(fig2, use_container_width=True)

# === QUẢN LÝ NGƯỜI DÙNG ===
elif menu == "👥 Quản lý người dùng":
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

# === CẤU HÌNH HỆ THỐNG ===
elif menu == "⚙️ Cấu hình hệ thống":
    st.subheader("⚙️ Cấu hình chung (mock demo)")
    st.write("Chức năng này sẽ cho phép thay đổi tham số hệ thống, như:")
    st.markdown("""
    - Đường dẫn lưu file OCR  
    - Bật/tắt cache AI  
    - Chọn mô hình AI trả lời (PhoGPT, llama.cpp, v.v.)
    """)
    st.info("Đây là phần mở rộng tuỳ chọn – chưa cần triển khai ở giai đoạn này.")

