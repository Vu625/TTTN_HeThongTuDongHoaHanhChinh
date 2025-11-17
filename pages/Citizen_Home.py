# check_role("citizen")
# st.title("🏠 Trang chủ Công dân")
#
# menu = st.sidebar.radio("Chức năng", ["Hồ sơ đã gửi","Nộp hồ sơ", "💬 Chatbot Hành chính AI"])
#
# # === ChatBot ===
# if menu == "💬 Chatbot Hành chính AI":
#     st.subheader("💬 Hỏi đáp thủ tục hành chính thông minh")
#     st.write("Bạn có thể hỏi như:")
#     st.info("• Tôi muốn cấp lại CCCD thì cần gì?\n• Đăng ký khai sinh trong bao lâu?\n• Hồ sơ chứng thực gồm gì?")
#
#     user_input = st.text_input("Nhập câu hỏi của bạn:")
#     if st.button("Gửi câu hỏi") and user_input.strip():
#         with st.spinner("Đang tra cứu văn bản pháp luật..."):
#             answer = generate_answer(user_input)
#         st.success("Kết quả:")
#         st.markdown(answer)
#
# # === Nộp hồ sơ ===
# if menu == "Nộp hồ sơ":
#     st.switch_page("pages/Submit_Application.py")
#
# # === Lịch sử hồ sơ ===
# if menu == "Hồ sơ đã gửi":
#     st.subheader("📚 Hồ sơ của bạn")
#     apps = load_applications()
#     user_apps = [a for a in apps if a["citizen_id"] == st.session_state["user_id"]]
#
#     if not user_apps:
#         st.info("Bạn chưa gửi hồ sơ nào")
#     else:
#         for a in user_apps:
#             steps = get_workflow_for_procedure(a["form_template_id"])
#             current_step = a.get("current_step", 1)
#             st.write(f"""
#                 **Mã hồ sơ:** {a['application_id']}
#                 **Thủ tục:** {get_name_form(a['form_template_id'])}
#                 **Bước hiện tại:** {steps[current_step-1]['title'] if steps else 'Không xác định'}
#                 **Trạng thái:** {a['status']}
#                 **Ngày gửi:** {a['submitted_at']}
#             """)
#             # hiển thị tiến độ
#             st.progress(current_step / len(steps) if steps else 0)
#             st.divider()
#
# if st.sidebar.button("Đăng xuất"):
#     logout()
#
#
import streamlit as st
from services.layout import load_common_layout
from services.auth_service import check_role
# check_role("citizen")
page = load_common_layout()

st.set_page_config(page_title="Công dân - VNeID", layout="wide")

# Gọi layout sidebar chung

# Giao diện chính theo menu
st.title("👨‍🌾 Trang công dân")

if page == "🏠 Trang chủ":
    # st.switch_page("pages/Citizen_Home")
    st.subheader("Trang chủ của công dân")
    st.write("Chào mừng bạn đến với hệ thống quản lý dân cư.")
elif page == "📰 Nộp Hồ Sơ":
    st.switch_page("pages/Submit_Application.py")
    # st.subheader("Tin tức")
    # st.write("Cập nhật các thông tin mới nhất...")
elif page == "🏢 Tổ chức":
    st.subheader("Tổ chức địa phương")
    st.write("Thông tin về các tổ chức, đoàn thể...")
elif page == "⚙️ Cài đặt":
    st.subheader("Cài đặt tài khoản")
    st.write("Chỉnh sửa thông tin cá nhân, mật khẩu, bảo mật...")
elif page == "🔔 Thông báo":
    st.switch_page("pages/4_🔔_Citizen_Notifications.py")

# Định nghĩa CSS cho Thanh bên (Sidebar) mới và Header
CUSTOM_CSS = """
<style>
/* 1. CSS Cho Header */
.header {
    background-color: #B71C1C; /* đỏ đậm */
    padding: 10px 30px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: white;
    border-bottom: 4px solid #FFD54F;
}
.header-left {
    display: flex;
    align-items: center;
}
.header-left img {
    width: 55px;
    margin-right: 10px;
}
.header-right {
    display: flex;
    align-items: center;
    gap: 15px;
    font-size: 16px;
}
.avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: white;
    color: #B71C1C;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* 2. CSS Cho Sidebar Tùy chỉnh */
/* Áp dụng màu nền be/hồng nhạt cho toàn bộ sidebar, như trong ảnh bạn gửi */
[data-testid="stSidebar"] {
    background-color: #fbf8f5 !important; 
    padding: 20px 0 !important;
}

/* Kiểu cho mỗi mục trong thanh bên */
.sidebar-item {
    text-align: center;
    cursor: pointer;
    margin: 10px auto; /* căn giữa và tạo khoảng cách */
    padding: 20px 10px;
    border-radius: 8px;
    transition: background-color 0.3s, color 0.3s;
    color: #4B4B4B; /* Màu chữ mặc định hơi xám */
    font-size: 18px;
    font-weight: 500;
}

.sidebar-item:hover {
    background-color: #f0f2f6; /* Hover nhẹ nhàng */
    color: #262730; /* Màu chữ đậm hơn khi hover */
}

/* Biểu tượng (Icon) */
.sidebar-item .icon {
    display: block;
    font-size: 30px;
    margin-bottom: 5px;
    /* Căn chỉnh icon và chữ để mô phỏng ảnh bạn gửi */
    color: inherit; 
}

/* Custom CSS cho st.button để mô phỏng click và active */
/* Tùy chỉnh button để căn giữa và tạo hiệu ứng Active */
div.stButton > button {
    width: 100%;
    text-align: center;
    border: none;
    background-color: transparent !important;
    color: #4B4B4B;
    font-size: 18px;
    font-weight: 500;
    padding: 20px 10px;
}

div.stButton > button:hover {
    background-color: #f0f2f6 !important;
    color: #262730 !important;
}

/* Class active được thêm vào thông qua HTML/Markdown để đánh dấu mục đang chọn */
.sidebar-active-btn button {
    background-color: #ffffff !important; /* Nền trắng khi Active */
    color: #B71C1C !important; /* Màu chữ đỏ đậm khi Active */
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Thêm box shadow để nổi bật */
}

/* Điều chỉnh lại khoảng cách và bố cục của st.button trong sidebar */
[data-testid="stSidebar"] div.stButton {
    margin-top: 5px;
}

</style>
"""

# Dictionary để ánh xạ tên trang sang Biểu tượng (Icon)
PAGES = {
    # "Trang chủ": "🏠",
    # "Tin tức": "📰",
    # "Tổ chức": "🏢",
    # "Cài đặt": "⚙️"
}


# 🧭 1. Thanh tiêu đề (Header) - Đã tối giản
def header(username):
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)  # Áp dụng CSS
    st.markdown(
        f"""
        <div class="header">
            <div class="header-left">
                <img src="https://play-lh.googleusercontent.com/k2J4mfmUj040c4dKuVwAg4CwR_4k_RRTO_Zb3a8dMGRynKTaUjek3P_i_MKjmFPG87uK=w480-h960-rw">
                <div>
                    <div style="font-weight:bold; font-size:18px;">BỘ CÔNG AN</div>
                    <div style="font-size:14px;">TRUNG TÂM DỮ LIỆU QUỐC GIA VỀ DÂN CƯ</div>
                </div>
            </div>
            <div class="header-right">
                <span>🔔</span>
                <span>{username}</span>
                <div class="avatar">👤</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# 📂 2. Thanh điều hướng bên trái (Sidebar) - Đã tùy chỉnh giao diện
def sidebar():
    # Khởi tạo trạng thái trang nếu chưa có
    if "page" not in st.session_state:
        st.session_state["page"] = "Trang chủ"

    # st.sidebar.markdown(f'<div style="text-align:center; font-weight:bold; font-size:24px; color:#B71C1C;">MENU</div>',
    #                     unsafe_allow_html=True)

    # Lặp qua các trang và tạo nút tùy chỉnh
    for page_name, icon in PAGES.items():
        is_active = st.session_state["page"] == page_name

        # Tạo HTML để mô phỏng bố cục Icon trên, chữ dưới
        # Lưu ý: Vì Streamlit st.button chỉ hỗ trợ markdown inline, ta phải sử dụng một trick CSS.

        # Thêm class 'sidebar-active-btn' nếu là trang đang chọn
        active_class = "sidebar-active-btn" if is_active else ""

        # Bố cục nút
        button_html = f"""
        <div class='sidebar-item {active_class}'>
            <span class='icon'>{icon}</span>
            <div style='line-height:1.2;'>{page_name}</div>
        </div>
        """

        # Streamlit không cho phép bắt click trực tiếp trên markdown.
        # Ta sẽ dùng st.button để bắt click và áp dụng CSS tùy chỉnh.

        button_clicked = st.sidebar.button(
            label=f"{icon} {page_name}",
            key=f"nav_{page_name}",
            use_container_width=True
        )

        # Vì st.button không hoàn toàn căn giữa được icon/text như ảnh,
        # giải pháp tốt nhất là thay thế bằng HTML button hoàn toàn.
        # Tuy nhiên, ta sẽ dùng st.markdown với <a> tag và query params để bắt click

        # *********** Thay thế st.sidebar.button bằng st.sidebar.markdown (Tùy chọn tốt hơn) ***********
        # Để đảm bảo giao diện chính xác, ta dùng link và bắt trạng thái (cần rerunning)
        st.sidebar.markdown(
            f"""
            <a href="?page={page_name}" style="text-decoration:none;">
                <div class='sidebar-item {'sidebar-active-btn' if st.session_state["page"] == page_name else ''}'>
                    <span class='icon'>{icon}</span>
                    {page_name}
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )

        # Xử lý click (Nếu bạn muốn dùng st.button để tránh rerunning quá nhiều)
        if button_clicked:
            st.session_state["page"] = page_name
            st.rerun()  # Bắt buộc phải rerun để thay đổi nội dung

    # Kiểm tra query parameter để cập nhật trạng thái nếu người dùng click vào <a> tag
    query_params = st.query_params
    if "page" in query_params and query_params["page"][0] in PAGES:
        st.session_state["page"] = query_params["page"][0]

    return st.session_state["page"]


# 💬 3. Nội dung chính
def main_content(user, page):
    full_name = user.get("full_name", "Người dùng")

    if page == "Trang chủ":
        st.markdown(
            f"""
            <h2>👋 Xin chào, {full_name}</h2>
            <p>Chào mừng bạn đến với <b>Trang thông tin định danh điện tử</b>.</p>
            """,
            unsafe_allow_html=True,
        )

        # Dùng HTML/CSS để có màu nền và nút như ảnh ban đầu (Dark Mode)
        st.markdown(
            """
            <style>
            .info-box {
                padding: 20px;
                border-radius: 10px;
                color: white;
                margin-bottom: 20px;
                min-height: 180px; /* Đảm bảo chiều cao đồng đều */
            }
            .news-box { background-color: #0077B6; } /* Xanh đậm */
            .alert-box { background-color: #FFC300; color: #333; } /* Vàng đậm */
            .faq-box { background-color: #2ECC71; } /* Xanh lá đậm */
            .box-title { font-weight: bold; font-size: 20px; margin-bottom: 10px; }
            .box-button { 
                background-color: #ffffff; 
                color: #B71C1C; 
                border-radius: 5px; 
                padding: 8px 15px; 
                border: none;
                cursor: pointer;
                float: right;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div class="info-box news-box">
                    <div class="box-title">📰 Tin tức – Sự kiện</div>
                    Cập nhật các tin nổi bật mới nhất trong ngày.
                    <br><br><br>
                    <button class="box-button">Xem ngay</button>
                </div>
            """, unsafe_allow_html=True)
            # st.button("Xem ngay", key="news") # Đã ẩn

        with col2:
            st.markdown("""
                <div class="info-box alert-box">
                    <div class="box-title">⚠️ Cảnh báo lừa đảo</div>
                    Cảnh báo mới nhất từ Bộ Công an.
                    <br><br><br>
                    <button class="box-button" style="color:#333;">Xem ngay</button>
                </div>
            """, unsafe_allow_html=True)
            # st.button("Xem ngay", key="alert") # Đã ẩn

        with col3:
            st.markdown("""
                <div class="info-box faq-box">
                    <div class="box-title">💬 Câu hỏi thường gặp</div>
                    Tổng hợp các thắc mắc phổ biến về VNeID.
                    <br><br><br>
                    <button class="box-button">Xem ngay</button>
                </div>
            """, unsafe_allow_html=True)
            # st.button("Xem ngay", key="faq") # Đã ẩn

    else:
        st.header(f"Nội dung trang: {page}")
        st.info(f"Đây là trang **{page}**. Nội dung chi tiết sẽ được phát triển tại đây.")


# ⚓ 4. Chân trang (Footer)
def footer():
    st.markdown(
        """
        <hr>
        <div style="text-align:center; font-size:14px; color:gray;">
            <a href="#" style="color:gray;">Câu hỏi thường gặp</a> |
            <a href="#" style="color:gray;">Điều khoản sử dụng</a> |
            <a href="#" style="color:gray;">Chính sách quyền riêng tư</a>
            <br><br>
            © Bản quyền thuộc về <b>Trung tâm Dữ liệu Quốc gia về Dân Cư – Bộ Công An</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


# 🚀 Gọi hàm hiển thị giao diện
def app():
    # 🟡 Giả lập đã đăng nhập
    if "current_user" not in st.session_state:
        st.session_state["current_user"] = {"full_name": "Nguyễn Văn A"}
    if "page" not in st.session_state:
        st.session_state["page"] = "Trang chủ"

    user = st.session_state["current_user"]
    full_name = user.get("full_name", "Người dùng")

    # Hiển thị Thanh bên (Sidebar)
    page = sidebar()

    # Hiển thị Header
    header(full_name)

    # Hiển thị Nội dung chính
    main_content(user, page)

    # Hiển thị Footer
    footer()


# Khi chạy độc lập file này (test)
if __name__ == "__main__":
    app()

