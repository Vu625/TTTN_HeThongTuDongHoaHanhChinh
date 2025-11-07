# import streamlit as st
# from services.auth_service import check_role, logout
# from services.data_viz_service import load_applications
#
# check_role("officer")
# if st.sidebar.button("Đăng xuất"):
#     logout()
# st.title("📥 Danh sách hồ sơ chờ xử lý")
#
# apps = load_applications()
#
# if not apps:
#     st.info("Chưa có hồ sơ nào")
# else:
#     for a in apps:
#         st.write(f"""
#             **Mã hồ sơ**: {a['application_id']}
#             **Người nộp**: {a['citizen_id']}
#             **Thủ tục**: {a['form_template_id']}
#             **Ngày gửi**: {a['submitted_at']}
#             **Trạng thái**: {a['status']}
#         """)


import streamlit as st
from services.auth_service import check_role
from services.data_viz_service import load_applications, save_applications, get_workflow_for_procedure , user_full_name , get_name_form
from pathlib import Path
from services.workflow_service import ACTIONS

check_role("officer")
st.title("🧾 Xử lý hồ sơ công dân")

# apps = load_applications()
#
# if not apps:
#     st.info("Chưa có hồ sơ nào được gửi")
# else:
#     selected = st.selectbox(
#         "Chọn hồ sơ cần xem:",
#         options=[f"{a['application_id']} - {a['form_template_id']}" for a in apps]
#     )
#
#     app = next(a for a in apps if a['application_id'] in selected)
#
#     st.write(f"**Người nộp:** {app['citizen_id']}")
#     st.write(f"**Loại thủ tục:** {app['form_template_id']}")
#     st.write(f"**Ngày gửi:** {app['submitted_at']}")
#     st.write(f"**Trạng thái hiện tại:** {app['status']}")
#     st.divider()
#
#     st.subheader("📎 Tài liệu đính kèm")
#
#     for doc_path in app["documents"]:
#         path = Path(doc_path)
#         if not path.exists():
#             st.warning(f"Không tìm thấy file: {path}")
#             continue
#
#         st.image(str(path), caption=path.name, width=400)
#         if st.button(f"🔍 Chạy OCR cho {path.name}"):
#             text = extract_text(path)
#             st.text_area(f"Nội dung OCR ({path.name})", text, height=200)
#             if "ocr_texts" not in app:
#                 app["ocr_texts"] = {}
#             app["ocr_texts"][path.name] = text
#
#     st.divider()
#     new_status = st.selectbox(
#         "Cập nhật trạng thái hồ sơ:",
#         options=["submitted", "verifying", "approved", "rejected"],
#         index=["submitted", "verifying", "approved", "rejected"].index(app["status"])
#     )
#
#     if st.button("💾 Lưu cập nhật"):
#         app["status"] = new_status
#         save_applications(apps)
#         st.success("Đã lưu trạng thái mới!")



# apps = load_applications()
# if not apps:
#     st.info("Chưa có hồ sơ nào được gửi")
# else:
#     selected = st.selectbox(
#         "Chọn hồ sơ cần xem:",
#         options=[f"{a['application_id']} - {a['form_template_id']}" for a in apps]
#     )
#     app = next(a for a in apps if a['application_id'] in selected)
#     steps = get_workflow_for_procedure(app["workflow_id"])
#     current_step = app.get("current_step", 1)
#     st.subheader(f"🪜 Bước hiện tại: {steps[current_step-1]['title']} ({current_step}/{len(steps)})")
#
#     st.write(f"**Người nộp:** {app['citizen_id']}")
#     st.write(f"**Trạng thái:** {app['status']}")
#     st.divider()
#
#     if current_step < len(steps):
#         next_title = steps[current_step]["title"]
#         if st.button(f"✅ Hoàn tất bước '{steps[current_step-1]['title']}' / chuyển sang '{next_title}'"):
#             app["current_step"] = current_step + 1
#             app["status"] = "verifying" if current_step < len(steps)-1 else "approved"
#             save_applications(apps)
#             st.success(f"Đã chuyển hồ sơ sang bước '{next_title}'")
#             st.rerun()
#     else:
#         st.success("🎉 Hồ sơ đã hoàn thành toàn bộ quy trình!")


apps = load_applications()

if not apps:
    st.info("Chưa có hồ sơ nào được gửi")
else:
    selected = st.selectbox(
        "Chọn hồ sơ cần xem:",
        options=[f"{a['application_id']} - {get_name_form(a['form_template_id'])}" for a in apps]
    )

    app = next(a for a in apps if a['application_id'] in selected)
    steps = get_workflow_for_procedure(app["form_template_id"])
    current_step = app.get("current_step", 1)
    step_data = steps[current_step - 1]
    st.subheader(f"🪜 Bước {current_step}/{len(steps)}: {step_data['title']}")
    st.write(f"**Người nộp:** {user_full_name(app['citizen_id'])}")
    st.write(f"**Trạng thái:** {app['status']}")
    st.divider()

    # === Gọi hành động tương ứng ===
    action_name = step_data.get("action")
    if action_name and action_name in ACTIONS:
        app = ACTIONS[action_name](app)
    else:
        st.info("Không có hành động đặc biệt cho bước này.")

    st.divider()

    # === Điều hướng workflow ===
    if current_step < len(steps):
        next_title = steps[current_step]["title"]
        if st.button(f"➡️ Chuyển sang '{next_title}'"):
            app["current_step"] = current_step + 1
            save_applications(apps)
            st.success(f"Đã chuyển sang bước '{next_title}'")
            st.rerun()
    else:
        st.success("🎉 Hồ sơ đã hoàn tất toàn bộ quy trình!")