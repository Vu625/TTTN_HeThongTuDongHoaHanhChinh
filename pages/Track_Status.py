import streamlit as st
from services.data_viz_service import load_applications,get_workflow_for_procedure,get_name_form
st.subheader("📚 Hồ sơ của bạn")
apps = load_applications()
user_apps = [a for a in apps if a["citizen_id"] == st.session_state["user_id"]]
st.divider()
if not user_apps:
    st.info("Bạn chưa gửi hồ sơ nào")
else:
    for a in user_apps:
        steps = get_workflow_for_procedure(a["form_template_id"])
        current_step = a.get("current_step", 1)
        st.write(f"""
                **Mã hồ sơ:** {a['application_id']} \n
                **Thủ tục:** {get_name_form(a['form_template_id'])} \n
                **Bước hiện tại:** {steps[current_step-1]['title'] if steps else 'Không xác định'} \n
                **Trạng thái:** {a['status']} \n
                **Ngày gửi:** {a['submitted_at']} \n
            """)
            # hiển thị tiến độ
        st.info(f"Tiến Độ {current_step}/{len(steps)}")
        st.progress(current_step / len(steps) if steps else 0)
        st.divider()