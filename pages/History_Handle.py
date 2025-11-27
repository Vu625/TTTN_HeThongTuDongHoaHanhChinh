# import streamlit as st
# from services.auth_service import check_role
# from services.data_viz_service import load_applications, name_status
# from services.layout import display_back_button
#
# check_role("officer")
# display_back_button()
# st.title("📜 Lịch sử hồ sơ đã xử lý")
#
# apps = load_applications()
#
# processed = [
#     a for a in apps
#     if a.get("basic_check_result") or a.get("approve_result")
# ]
#
# if not processed:
#     st.info("Chưa có hồ sơ nào được xử lý.")
#     st.stop()
#
# processed = sorted(
#     processed,
#     key=lambda x: x.get("updated_at", ""),
#     reverse=True
# )
#
# for app in processed:
#     st.markdown(f"""
#     ### 🗂 {app['application_id']} — {app['form_template_id']}
#     **Trạng thái:** {name_status(app['status'])}
#     """)
#     if app.get("approve_note"):
#         st.write(f"**Ghi chú:** {app['approve_note']}")
#     if app.get("reject_reason"):
#         st.write(f"**Lý do từ chối:** {app['reject_reason']}")
#
#     st.divider()
import streamlit as st
from services.auth_service import check_role
from services.data_viz_service import load_applications, name_status, get_name_form
from services.layout import display_back_button
from pathlib import Path

check_role("officer")
display_back_button()
st.title("📜 Lịch sử hồ sơ đã xử lý")

apps = load_applications()

# Lọc các hồ sơ đã qua basic_check hoặc approve_result
processed = [
    a for a in apps
    if a.get("basic_check_result") or a.get("approve_result")
]

if not processed:
    st.info("Chưa có hồ sơ nào được xử lý.")
    st.stop()

# Sắp xếp theo thời gian mới nhất
processed = sorted(
    processed,
    key=lambda x: x.get("updated_at", ""),
    reverse=True
)

st.markdown("### 🧾 Danh sách hồ sơ đã xử lý")

for app in processed:
    st.markdown(f"""
    ### 🗂   {get_name_form(app['form_template_id'])}—{app['application_id']}
    **Trạng thái:** {name_status(app['status'])}  
    """)
    if app.get("approve_note"):
        st.write(f"**Ghi chú:** {app['approve_note']}")
    if app.get("reject_reason"):
        st.write(f"**Lý do từ chối:** {app['reject_reason']}")

    # ========== NÚT XEM LẠI ==========
    view_key = f"view_{app['application_id']}"
    if st.button("👁 Xem lại", key=view_key):
        st.session_state[f"open_{app['application_id']}"] = True

    # ========== HIỂN THỊ CHI TIẾT (nếu đã click) ==========
    if st.session_state.get(f"open_{app['application_id']}", False):

        with st.expander("📄 Chi tiết hồ sơ", expanded=True):

            st.subheader("📌 Thông tin công dân đã gửi")
            st.json(app.get("form_data", {}))

            st.markdown("### 📎 Tài liệu đính kèm")

            docs = app.get("documents", [])
            if not docs:
                st.info("Không có tài liệu đính kèm.")
            else:
                for doc_path in docs:
                    p = Path(doc_path)
                    st.write(f"📄 **{p.name}**")

                    if not p.exists():
                        st.error(f"⚠️ File không tồn tại: {doc_path}")
                        continue

                    # Hiển thị hình ảnh
                    if p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                        st.image(str(p), width=350)

                    # Hiển thị PDF
                    elif p.suffix.lower() == ".pdf":
                        st.markdown("#### 📑 Xem PDF:")
                        try:
                            st.pdf(str(p))  # Streamlit >= 1.32
                        except:
                            st.markdown(
                                f"""
                                <iframe src="{str(p)}" width="100%" height="600px"></iframe>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.info(f"Không thể hiển thị trực tiếp file {p.suffix}")

                    st.markdown("---")

            st.subheader("🕓 Lịch sử xử lý")
            if app.get("basic_check_result"):
                st.write(f"• Kiểm tra ban đầu: **{app.get('basic_check_result')}**")
            if app.get("approve_result"):
                st.write(f"• Phê duyệt cuối: **{app.get('approve_result')}**")
            if app.get("approve_note"):
                st.write(f"• Ghi chú phê duyệt: {app.get('approve_note')}")
            if app.get("reject_reason"):
                st.write(f"• Lý do từ chối: {app.get('reject_reason')}")

            st.markdown("---")

            if st.button("Đóng", key=f"close_{app['application_id']}"):
                st.session_state[f"open_{app['application_id']}"] = False
                st.rerun()

    st.divider()
