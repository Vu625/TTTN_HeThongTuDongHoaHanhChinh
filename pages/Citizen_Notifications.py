import streamlit as st
from services.layout import display_back_button, init_notification_state
from services.auth_service import check_role

# Khởi tạo danh sách thông báo nếu chưa có
if "citizen_notifications" not in st.session_state:
    st.session_state.citizen_notifications = []

init_notification_state()

st.title("📨 Thông báo của bạn")

# display_back_button()

notifications = st.session_state.citizen_notifications

if not notifications:
    st.info("Bạn chưa có thông báo nào.")
else:
    for i, n in enumerate(notifications):
        box_color = {
            "success": "lightgreen",
            "error": "salmon",
            "info": "lightblue"
        }.get(n["type"], "white")

        with st.container():
            st.markdown(
                f"""
                <div style='padding:10px; border-radius:8px; background:{box_color}'>
                    <b>{n['message']}</b><br>
                    <small style='opacity:0.7'>Trạng thái: {"🔵 Chưa đọc" if not n["read"] else "⚪ Đã đọc"}</small>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Mark as read
            if not n["read"]:
                notifications[i]["read"] = True
