import streamlit as st
from services.auth_service import check_role
from services.data_viz_service import load_applications

check_role("officer")

st.title("📜 Lịch sử hồ sơ đã xử lý")

apps = load_applications()

processed = [
    a for a in apps
    if a.get("basic_check_result") or a.get("approve_result")
]

if not processed:
    st.info("Chưa có hồ sơ nào được xử lý.")
    st.stop()

processed = sorted(
    processed,
    key=lambda x: x.get("updated_at", ""),
    reverse=True
)

for app in processed:
    st.markdown(f"""
    ### 🗂 {app['application_id']} — {app['form_template_id']}
    **Trạng thái:** {app['status']}  
    """)
    if app.get("approve_note"):
        st.write(f"**Ghi chú:** {app['approve_note']}")
    if app.get("reject_reason"):
        st.write(f"**Lý do từ chối:** {app['reject_reason']}")

    st.divider()
