# pages/Change_Password.py
import streamlit as st
# Đảm bảo bạn import các hàm từ tệp dịch vụ đã sửa đổi
from services.auth_service import check_role, update_password
from services.layout import display_back_button

# Đặt tiêu đề và cấu hình trang
st.set_page_config(page_title="Đổi Mật Khẩu", layout="centered")

# Chỉ cho phép người dùng đã đăng nhập truy cập
check_role("citizen", "officer", "admin")
display_back_button()
st.title("🔐 Đổi Mật Khẩu")
st.subheader(f"Xin chào, {st.session_state.get('full_name')}!")

# Sử dụng st.form để xử lý việc nhập liệu và nút bấm
with st.form("change_password_form"):
    # Lấy ID người dùng hiện tại từ session state
    current_user_id = st.session_state.get("user_id")

    # Nhập mật khẩu mới
    new_password = st.text_input(
        "Nhập mật khẩu mới:",
        type="password",
        placeholder="Mật khẩu mới (ít nhất 6 ký tự)"
    )

    # Xác nhận mật khẩu mới
    confirm_password = st.text_input(
        "Xác nhận mật khẩu mới:",
        type="password",
        placeholder="Nhập lại mật khẩu mới"
    )

    # Nút submit form
    submitted = st.form_submit_button("Thay Đổi Mật Khẩu")

    if submitted:
        # 1. Kiểm tra tính hợp lệ
        if not new_password or not confirm_password:
            st.warning("Vui lòng nhập đầy đủ mật khẩu mới và xác nhận.")
        elif len(new_password) < 6:
            st.warning("Mật khẩu phải có ít nhất 6 ký tự.")
        elif new_password != confirm_password:
            st.error("Mật khẩu mới và mật khẩu xác nhận không khớp.")

        # 2. Xử lý cập nhật
        else:
            if update_password(current_user_id, new_password):
                st.success("✅ Thay đổi mật khẩu thành công! Mật khẩu đã được mã hóa và lưu.")
                # Có thể thêm logic logout hoặc chuyển hướng sau khi đổi mật khẩu
            else:
                st.error("❌ Lỗi: Không tìm thấy ID người dùng hoặc lỗi khi lưu.")

# Hiển thị thông tin người dùng hiện tại (Tùy chọn)
st.markdown("---")
st.caption(f"ID Người dùng: **{current_user_id}** | Quyền: **{st.session_state.get('role')}**")