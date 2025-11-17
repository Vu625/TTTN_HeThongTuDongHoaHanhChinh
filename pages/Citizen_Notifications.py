import streamlit as st
from services.auth_service import check_role
from services.data_viz_service import load_applications

check_role("citizen")

st.title("🔔 Thông báo hồ sơ")

apps = load_applications()
user_apps = [a for a in apps if a["citizen_id"] == st.session_state["user_id"]]

has_message = False

for app in user_apps:
    if app.get("basic_check_result") == "rejected":
        has_message = True
        st.error(f"""
        ### ❌ Hồ sơ bị từ chối
        **Mã hồ sơ:** {app['application_id']}  
        **Thủ tục:** {app['form_template_id']}  
        **Lý do:** {app.get('reject_reason', 'Không rõ')}  
        """)
        st.divider()

if not has_message:
    st.info("✨ Không có thông báo nào.")
