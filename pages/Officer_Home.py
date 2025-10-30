import streamlit as st
from services.auth_service import check_role, logout
from services.data_viz_service import load_applications

check_role("officer")
if st.sidebar.button("Đăng xuất"):
    logout()
st.title("📥 Danh sách hồ sơ chờ xử lý")

apps = load_applications()

if not apps:
    st.info("Chưa có hồ sơ nào")
else:
    for a in apps:
        st.write(f"""
            **Mã hồ sơ**: {a['application_id']}  
            **Người nộp**: {a['citizen_id']}  
            **Thủ tục**: {a['form_template_id']}  
            **Ngày gửi**: {a['submitted_at']}
            **Trạng thái**: {a['status']}
        """)
