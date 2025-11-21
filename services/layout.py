import streamlit as st
import streamlit.components.v1 as components
from services.auth_service import logout
from services.data_viz_service import load_applications
import os
def load_common_layout():
    """Hiển thị layout (sidebar) chung cho tất cả các trang."""
    with st.sidebar:
        # Logo hoặc biểu tượng
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712027.png", width=80)
        st.markdown("### 🇻🇳 Hệ thống VNeID")

        # Thông tin người dùng (nếu đã đăng nhập)
        username = st.session_state.get("username", "Khách")
        role = st.session_state.get("role", "Chưa xác định")

        st.markdown(f"👤 **{username}**")
        st.caption(f"Vai trò: {role}")
        st.markdown("---")

        # Menu điều hướng chung
        selected = st.radio(
            "📂 Danh mục",
            ["🏠 Trang chủ", "📰 Nộp Hồ Sơ", "🏢 Tổ chức", "⚙️ Cài đặt"],
            key="menu_sidebar"
        )

        st.markdown("---")
        if st.button("🚪 Đăng xuất"):
            logout()
            # st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("© 2025 VNeID Citizen System")

        # Trả về lựa chọn
        return selected


def display_back_button():
    """
    Hiển thị nút "Quay Lại" bằng st.page_link, trỏ đến Trang Chủ của người dùng
    (Citizen Home hoặc Admin Home) dựa trên Session State.
    """

    # 1. Xác định trang chủ dựa trên vai trò (Role) đã lưu trong session state
    role = st.session_state.get("role")

    if role == "citizen":
        home_page_path = "pages/Citizen_Home.py"
        label = "⬅️ Quay lại Trang Chủ Công Dân"
    elif role == "admin":
        # Giả sử admin muốn quay về Dashboard
        home_page_path = "pages/Admin_Dashboard.py"
        label = "⬅️ Quay lại Bảng Điều Khiển Admin"
    elif role == "officer":
        home_page_path = "pages/Officer_Home.py"
        label = "⬅️ Quay lại Trang Cán bộ"
    else:
        # Mặc định hoặc khi chưa đăng nhập
        # app.py thường là trang đăng nhập hoặc trang giới thiệu
        home_page_path = "app.py"
        label = "⬅️ Quay lại Trang Chủ"

    # 2. Hiển thị nút page_link
    # st.markdown("---")  # Thêm một đường kẻ để tách biệt nút
    st.page_link(
        home_page_path,
        label=label,
        # icon="🏠"
    )
# def add_notification(message, ntype="info"):
#     """
#     ntype = 'success', 'error', 'info'
#     """
#     st.session_state.citizen_notifications.append({
#         "message": message,
#         "type": ntype,
#         "read": False
#     })
#
# def init_notification_state():
#     if "citizen_notifications" not in st.session_state:
#         st.session_state.citizen_notifications = []
def init_notification_state():
    if "citizen_notifications" not in st.session_state:
        st.session_state.citizen_notifications = []

def notification_bell():
    # unread = sum(1 for n in st.session_state.citizen_notifications if not n["read"])
    user_id = st.session_state["user_id"]
    apps = load_applications()

    unread = sum(1 for a in apps
                 if a.get("notification")
                 and a["notification"].get("seen") == False
                 and a["citizen_id"] == user_id)
    return unread
    # components.html(
    #     f"""
    #     <div style="position: relative; display: inline-block; cursor:pointer;"
    #          onclick="window.location.href='?page=🔔+Thông+báo'">
    #         <span style="font-size: 22px;">🔔</span>
    #
    #         {f'''
    #         <span style="
    #             position: absolute;
    #             top: -5px;
    #             right: -5px;
    #             background: red;
    #             color: white;
    #             padding: 2px 6px;
    #             border-radius: 50%;
    #             font-size: 10px;
    #         ">{unread}</span>
    #         ''' if unread > 0 else ""}
    #     </div>
    #     """,
    #     height=40,
    # )

current_file_name = os.path.basename(__file__)
# Hàm kiểm tra và chuyển trang
def check_and_switch(col, button_text, page_file, key):
    is_current_page = (current_file_name == page_file)
    with col:
        if st.button(button_text, key=key, disabled=is_current_page):
            if page_file == "app.py":
                st.switch_page(page_file)
            else:
                st.switch_page(f"pages/{page_file}")