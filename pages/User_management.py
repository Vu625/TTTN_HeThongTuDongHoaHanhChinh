from services.data_viz_service import load_users, save_users
import streamlit as st
import pandas as pd
from services.layout import display_back_button
from services.auth_service import check_role, hash_password
import time
import uuid  # Cần thiết cho chức năng Thêm người dùng

# --- 1. KIỂM TRA QUYỀN VÀ KHỞI TẠO DỮ LIỆU ---
check_role("admin")
# Thao tác này sẽ stop nếu không phải admin
display_back_button()

# Tải dữ liệu người dùng
users = load_users()
df_users = pd.DataFrame(users)

# --- 2. HIỂN THỊ DANH SÁCH TÀI KHOẢN VÀ XÓA ---
st.subheader("📋 Danh sách tài khoản và Xóa")

if df_users.empty:
    st.info("Chưa có tài khoản nào được tạo.")
else:
    # HIỂN THỊ DANH SÁCH BẰNG CÁCH SỬ DỤNG st.columns và st.button (Phương pháp cũ)

    # 1. Hiển thị header
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 3, 1])
    col1.markdown("**ID**", unsafe_allow_html=True)
    col2.markdown("**Tên Đăng Nhập**", unsafe_allow_html=True)
    col3.markdown("**Vai Trò**", unsafe_allow_html=True)
    col4.markdown("**Họ Tên**", unsafe_allow_html=True)
    col5.markdown("", unsafe_allow_html=True)
    # st.markdown("---")

    # 2. Hiển thị từng hàng và nút Xóa
    for i, user in enumerate(users):
        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 3, 1])

        col1.text(user["user_id"])
        col2.text(user["username"])
        col3.text(user["role"])
        col4.text(user["full_name"])

        # Tạo nút Xóa riêng cho từng hàng với key duy nhất
        if col5.button("Xóa", key=f"delete_{user['user_id']}", help=f"Xóa người dùng {user['username']}"):

            # Xử lý sự kiện XÓA
            if user["user_id"] == st.session_state.get("user_id"):
                st.error("Không thể tự xóa tài khoản của chính mình!")
            else:
                del users[i]  # Xóa người dùng khỏi danh sách
                save_users(users)
                st.success(f"Đã xóa tài khoản '{user['full_name']}' thành công!")
                time.sleep(1)
                st.rerun()

# Nút tải lại (Giữ nguyên)
if st.button("Tải lại", key="reload_btn"):
    st.rerun()

# --- 3. CHỈNH SỬA TÀI KHOẢN HIỆN CÓ ---
st.divider()
st.subheader("✍️ Chỉnh sửa tài khoản")

# Tạo danh sách các ID người dùng để chọn
user_ids = [u["user_id"] for u in users]

# Chọn ID người dùng cần chỉnh sửa
selected_id = st.selectbox("Chọn ID người dùng cần chỉnh sửa:", user_ids, index=None, placeholder="Chọn ID...",
                           key="edit_selectbox")

if selected_id:
    # Tìm thông tin người dùng được chọn
    # Sử dụng next() để tìm người dùng đầu tiên khớp
    user_data = next((u for u in users if u["user_id"] == selected_id), None)

    # Lấy index ban đầu để có thể cập nhật chính xác trong danh sách 'users'
    original_index = users.index(user_data)

    if user_data:
        # Tạo Form chỉnh sửa
        with st.form("edit_user_form"):
            st.markdown(f"**Đang chỉnh sửa:** **{user_data['full_name']}** ({selected_id})")

            # Trường không cho phép chỉnh sửa (hiển thị)
            st.text_input("Tên đăng nhập", value=user_data["username"], disabled=True)

            # Trường cho phép chỉnh sửa
            new_full_name = st.text_input("Họ tên mới", value=user_data["full_name"])

            # Tìm index của vai trò hiện tại trong list ["citizen", "officer", "admin"]
            role_options = ["citizen", "officer", "admin"]
            current_role_index = role_options.index(user_data["role"]) if user_data["role"] in role_options else 0

            new_role = st.selectbox("Vai trò mới", role_options, index=current_role_index)

            # Mật khẩu mới (Tùy chọn)
            new_password_edit = st.text_input("Mật khẩu mới (Để trống nếu không muốn đổi)", type="password", value="")

            edited = st.form_submit_button("Lưu Thay Đổi")

            if edited:
                # 1. Kiểm tra không được chỉnh sửa vai trò của chính mình thành vai trò khác (tránh mất quyền truy cập)
                if selected_id == st.session_state.get("user_id") and new_role != user_data["role"]:
                    st.error("Bạn không thể tự thay đổi vai trò của chính mình!")
                    st.stop()

                # 2. Cập nhật dữ liệu
                user_data["full_name"] = new_full_name
                user_data["role"] = new_role

                # 3. Xử lý Mật khẩu mới (nếu có)
                if new_password_edit:
                    if len(new_password_edit) < 6:
                        st.error("Mật khẩu mới phải có ít nhất 6 ký tự.")
                        st.stop()
                    user_data["password"] = hash_password(new_password_edit)
                    st.success(f"Đã đổi mật khẩu cho **{user_data['username']}**.")

                # 4. Cập nhật danh sách và lưu
                users[original_index] = user_data
                save_users(users)
                st.success(f"Đã cập nhật thông tin cho **{user_data['full_name']}** thành công!")
                time.sleep(1)
                st.rerun()

# --- 4. THÊM NGƯỜI DÙNG MỚI (Đã thêm kiểm tra Tên đăng nhập và chuyển sang Form) ---
st.divider()
st.subheader("➕ Thêm người dùng mới")

with st.form("add_user_form"):
    # Đảm bảo dùng key khác cho các input này để tránh xung đột
    user_id = st.text_input("ID đăng nhập mới", key="add_user_id")
    username = st.text_input("Tên đăng nhập mới", key="add_username")
    password = st.text_input("Mật khẩu", type="password", key="add_password")
    role = st.selectbox("Vai trò", ["citizen", "officer", "admin"], key="add_role")
    full_name = st.text_input("Họ tên", key="add_full_name")

    add_submitted = st.form_submit_button("Thêm tài khoản")

    if add_submitted:
        # 1. Kiểm tra đầu vào
        if not username.strip() or not password.strip() or not full_name.strip() or not user_id.strip():
            st.error("Vui lòng nhập đầy đủ ID, Tên đăng nhập, Mật khẩu và Họ tên.")
        elif len(password) < 6:
            st.error("Mật khẩu phải có ít nhất 6 ký tự.")
        elif any(u["user_id"] == user_id for u in users):
            st.error(f"ID '{user_id}' đã tồn tại. Vui lòng nhập ID khác.")
        elif any(u["username"] == username for u in users):
            st.error(f"Tên đăng nhập '{username}' đã tồn tại. Vui lòng chọn tên khác.")

        # 2. THÊM NGƯỜI DÙNG
        else:
            new_user = {
                "user_id": user_id,
                "username": username,
                "password": hash_password(password),
                "role": role,
                "full_name": full_name
            }
            users.append(new_user)
            save_users(users)
            st.success(f"Đã thêm tài khoản '{full_name}' ({role}) thành công!")
            time.sleep(1)
            st.rerun()