# import streamlit as st
# from services.auth_service import check_role
# from services.data_viz_service import load_applications , get_name_form
# from services.layout import display_back_button
#
# # check_role("citizen")
# display_back_button()
# st.title("🔔 Thông báo hồ sơ")
#
# apps = load_applications()
# user_apps = [a for a in apps if a["citizen_id"] == st.session_state["user_id"]]
#
# has_message = False
#
# for app in user_apps:
#     if app.get("basic_check_result") == "rejected":
#         has_message = True
#         st.error(f"""
#         ### ❌ Hồ sơ bị từ chối
#         **Mã hồ sơ:** {app['application_id']}
#         **Thủ tục:** {get_name_form(app['form_template_id'])}
#         **Lý do:** {app.get('reject_reason', 'Không rõ')}
#         """)
#         st.divider()
#     if app.get("status") == "approved":
#         has_message = True
#         st.success(f"""
#             ### ✅ Hồ sơ đã được xử lý hoàn tất
#             **Mã hồ sơ:** {app['application_id']}
#             **Thủ tục:** {get_name_form(app['form_template_id'])}
#             """)
#
#         note = app.get("approve_note")
#         if note:
#             st.info(f"**Ghi chú từ cán bộ:** {note}")
#         st.divider()
#
# if not has_message:
#     st.info("✨ Không có thông báo nào.")

########################################################################
import streamlit as st
from services.auth_service import check_role
from services.data_viz_service import load_applications, save_applications , get_name_form
from datetime import datetime
from services.layout import display_back_button
check_role("citizen")
display_back_button()
st.title("🔔 Thông báo hồ sơ")

apps = load_applications()
user_id = st.session_state["user_id"]

# Lọc thông báo của người dùng
user_apps = [
    a for a in apps
    if a.get("notification") and a["citizen_id"] == user_id
]

# Nếu không có thông báo
if not user_apps:
    st.info("✨ Không có thông báo nào.")
    st.stop()

# Sắp xếp:
# 1. Chưa xem trước
# 2. Đã xem sau
# 3. Mới nhất ở trên
user_apps.sort(
    key=lambda x: (
        x["notification"]["seen"],           # False trước, True sau
        x["notification"]["time"]            # Sort newest → oldest
    ),
    reverse=True
)

# for app in user_apps:
#
#     notif = app["notification"]
#     notif_type = notif["type"]       # approved / rejected
#     seen = notif["seen"]
#     message = notif["message"]
#
#     # Khung màu
#     if notif_type == "approved":
#         box = st.success if not seen else st.info
#         title = "Hồ sơ đã được xử lý hoàn tất"
#     else:
#         box = st.error if not seen else st.info
#         title = "Hồ sơ bị từ chối"
#
#     with box(
#         f"""
#         ### {title}
#         **Mã hồ sơ:** {app['application_id']}  \n
#         **Thủ tục:** {app['form_template_id']}  \n
#         **Thời gian:** {notif['time']} \n
#         """
#     ):
#         btn_label = "Xem ngay" if not seen else "Xem lại"
#
#         if st.button(btn_label, key=f"view_{app['application_id']}"):
#             with st.expander("📄 Nội dung thông báo", expanded=True):
#                 st.write(message)
#
#             # Đánh dấu đã xem
#             notif["seen"] = True
#             save_applications(apps)
for app in user_apps:
    notif = app["notification"]
    notif_type = notif["type"]
    seen = notif["seen"]
    message = notif["message"]

    # 1. Xác định loại box và Icon
    if notif_type == "approved":
        box = st.success if not seen else st.info
        title_text = "✅ Hồ sơ đã được xử lý hoàn tất"
    else:
        box = st.error if not seen else st.info
        title_text = "⛔ Hồ sơ bị từ chối"

    # 2. Bắt đầu khối giao diện
    # Chỉ truyền Tiêu đề vào hàm box()
    with box(title_text):

        c1, c2 = st.columns([8, 2])
        with c1:
            st.markdown(
                f"""
                ### :blue[***{title_text}***] \n 
                **Mã hồ sơ:** `{app['application_id']}`  
                **Thủ tục:** {app['form_template_id']}  
                **Thời gian:** {notif['time']}
                """
            )

        with c2:
            # Căn chỉnh nút bấm cho đẹp
            st.write("")  # Hack nhỏ để đẩy nút xuống giữa dòng nếu cần
            btn_label = "Chưa Xem!" if not seen else "Xem lại"

            # Logic nút bấm
            if st.button(btn_label, key=f"view_{app['application_id']}", use_container_width=True):
                # Toggle trạng thái xem chi tiết
                st.session_state[f"show_details_{app['application_id']}"] = \
                    not st.session_state.get(f"show_details_{app['application_id']}", False)

                # Cập nhật trạng thái 'seen' nếu chưa xem
                if not seen:
                    notif["seen"] = True
                    save_applications(apps)
                    st.rerun()  # Load lại trang để đổi màu thông báo ngay lập tức

        # Hiển thị nội dung chi tiết (nếu đã bấm nút)
        # Mẹo: Dùng session_state để kiểm soát việc mở/đóng nội dung thay vì lồng vào st.button (vì st.button sẽ reset sau khi click chỗ khác)
        if st.session_state.get(f"show_details_{app['application_id']}", False):
            with st.expander("📄 Nội dung chi tiết", expanded=True):
                st.write(message)
                # Nút đóng lại nếu cần
                if st.button("Đóng", key=f"close_{app['application_id']}"):
                    st.session_state[f"show_details_{app['application_id']}"] = False
                    st.rerun()
    st.divider()
