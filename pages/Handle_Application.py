import streamlit as st
from services.auth_service import check_role
from services.data_viz_service import load_applications, save_applications, get_workflow_for_procedure , user_full_name , get_name_form, name_status
from pathlib import Path
from services.workflow_service import ACTIONS
from services.layout import display_back_button

check_role("officer")
display_back_button()
st.title("🧾 Xử lý hồ sơ công dân")
apps = load_applications()

if not apps:
    st.info("Chưa có hồ sơ nào được gửi")
else:
    selected = st.selectbox(
        "Chọn hồ sơ cần duyệt:",
        options=[f"{get_name_form(a['form_template_id'])} - Công Dân {user_full_name(a['citizen_id'] )} - {a['application_id']}" for a in apps if a ['status']=="submitted"]
    )

    app = next(a for a in apps if a['application_id'] in selected)
    steps = get_workflow_for_procedure(app["form_template_id"])
    current_step = app.get("current_step", 1)
    step_data = steps[current_step - 1]
    st.subheader(f"🪜 Bước {current_step}/{len(steps)}: {step_data['title']}")
    st.write(f"**Người nộp:** {user_full_name(app['citizen_id'])}")
    st.write(f"**Trạng thái:** {name_status(app['status'])}")
    st.divider()

    # === Gọi hành động tương ứng ===
    action_name = step_data.get("action")
    if action_name and action_name in ACTIONS:
        app = ACTIONS[action_name](app)
        save_applications(apps)
    else:
        st.info("Không có hành động đặc biệt cho bước này.")

    st.divider()

    # === Điều hướng workflow ===

    # if current_step < len(steps):
    #     next_title = steps[current_step]["title"]
    #     if st.button(f"➡️ Chuyển sang '{next_title}'"):
    #         app["current_step"] = current_step + 1
    #         save_applications(apps)
    #         st.success(f"Đã chuyển sang bước '{next_title}'")
    #         st.rerun()
    # else:
    #     st.success("🎉 Hồ sơ đã hoàn tất toàn bộ quy trình!")

    if app.get("basic_check_result") == "rejected":
        st.error("Hồ sơ đã bị từ chối. Không thể chuyển bước.")
    else:
        if current_step < len(steps):
            next_title = steps[current_step]["title"]
            if st.button(f"➡️ Chuyển sang '{next_title}'"):
                app["current_step"] = current_step + 1
                save_applications(apps)
                st.success(f"Đã chuyển sang bước '{next_title}'")
                st.rerun()
        else:
            st.success("🎉 Hồ sơ đã hoàn tất toàn bộ quy trình!")