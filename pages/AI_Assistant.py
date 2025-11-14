import streamlit as st
from services.llm_inference import ask_lmstudio
import time

st.set_page_config(page_title="Trợ lý ảo", layout="wide")

SIDEBAR_WIDTH = 280
PRIMARY_COLOR = "#007bff"

# Danh sách các câu hỏi gợi ý
SUGGESTION_PROMPTS = [
    "Hỏi về CCCD gắn chip",
    "Đổi ảnh trên VNeID",
    "Vấn đề xác thực tài khoản",
    "Hướng dẫn làm thủ tục hành chính online"
]


# --- Hàm Callback và Logic ---
def on_suggest_click(prompt):
    """Cập nhật state khi click gợi ý."""
    st.session_state.suggest_clicked = True
    st.session_state.suggest_prompt = prompt


# def handle_prompt(prompt):
#     """Xử lý logic gửi tin nhắn chung."""
#     if not prompt.strip():
#         return
#
#     st.session_state.messages.append(("user", prompt))
#
#     with st.spinner("Trợ lý đang phản hồi..."):
#         time.sleep(1)
#
#     st.session_state.messages.append(("bot", f"Tôi đã nhận được: '{prompt}'"))
#
#     st.session_state.history.append(prompt)
#     st.session_state.history = st.session_state.history[-10:]
#     st.session_state.input_key += 1  # Thay đổi key để xóa input box
#     st.rerun()

# def handle_prompt(prompt):
#     """Xử lý logic gửi tin nhắn chung."""
#     if not prompt.strip():
#         return
#
#     # 1. Thêm tin nhắn người dùng vào state
#     st.session_state.messages.append(("user", prompt))
#
#     # 2. Hiển thị spinner và gọi hàm LM Studio
#     with st.spinner("Trợ lý đang phản hồi..."):
#         # **********************************************
#         # *** CHỈNH SỬA Ở ĐÂY: GỌI HÀM LM STUDIO ***
#         # **********************************************
#         bot_response = ask_lmstudio(prompt)
#         # **********************************************
#
#     # 3. Thêm phản hồi của bot vào state
#     st.session_state.messages.append(("bot", bot_response))
#
#     # 4. Cập nhật lịch sử và xóa input box
#     st.session_state.history.append(prompt)
#     st.session_state.history = st.session_state.history[-10:]
#     st.session_state.input_key += 1
#     st.rerun() # Quan trọng để làm mới giao diện
def handle_prompt(prompt):
    """Xử lý logic gửi tin nhắn chung và buộc làm mới giao diện."""
    if not prompt.strip():
        return

    # 1. Thêm tin nhắn người dùng vào state
    st.session_state.messages.append(("user", prompt))

    # 2. Hiển thị spinner và gọi hàm LM Studio
    with st.spinner("Trợ lý đang phản hồi..."):
        # Đảm bảo hàm ask_lmstudio chỉ trả về chuỗi, không print ra terminal
        bot_response = ask_lmstudio(prompt)

    # 3. Thêm phản hồi của bot vào state
    st.session_state.messages.append(("bot", bot_response))

    # 4. Cập nhật lịch sử và quan trọng nhất là TĂNG KEY
    st.session_state.history.append(prompt)
    st.session_state.history = st.session_state.history[-10:]
    st.session_state.input_key += 1
    st.rerun()

# --- Khởi tạo Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "suggest_clicked" not in st.session_state:
    st.session_state.suggest_clicked = False
if "suggest_prompt" not in st.session_state:
    st.session_state.suggest_prompt = None
# Khởi tạo key cho input box trung tâm
if "initial_input_box" not in st.session_state:
    st.session_state.initial_input_box = ""

# Logic xử lý Gợi ý (Nằm ngoài callback)
# if st.session_state.suggest_clicked:
#     handle_prompt(st.session_state.suggest_prompt)
#     st.session_state.suggest_clicked = False
#     st.session_state.suggest_prompt = None
#     del st.session_state["suggest_clicked"]
if st.session_state.suggest_clicked:
    # 1. RESET NGAY LẬP TỨC: Đảm bảo flag lặp vô tận được tắt ngay trước khi gọi handle_prompt
    temp_prompt = st.session_state.suggest_prompt
    st.session_state.suggest_clicked = False
    st.session_state.suggest_prompt = None

    # 2. XỬ LÝ PROMPT: Gọi handle_prompt với prompt đã lưu
    # Hàm này sẽ chạy logic AI và gọi st.rerun()
    handle_prompt(temp_prompt)
# ======== 1. CSS Tối ưu ==========
st.markdown(f"""
    <style>
    /* Reset và Cấu hình chung */
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{ display: none !important; }}
    [data-testid="stAppViewContainer"] {{ background-color: white; }}
    /*[data-testid="stVerticalBlock"] {{ height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}*/

    /* 2. CSS Sidebar */
    [data-testid="stSidebar"] {{
        width: {SIDEBAR_WIDTH}px !important;
        background-color: white !important;
        padding: 10px 10px 10px 20px !important; 
        border-right: 1px solid #ddd;
        min-width: {SIDEBAR_WIDTH}px !important;
        overflow-y: auto;
    }}
    .new-chat-btn-container button {{ background-color: {PRIMARY_COLOR}; color: white; text-align: center; padding: 12px 0; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; width: 100%; border: none; font-size: 1rem; }}

    /* 3. CSS Khu vực Chat Chính */
    .chat-box {{ flex-grow: 1; overflow-y: auto; padding: 20px 24px; background-color: #f8f9fa; }}
    /* Định dạng tin nhắn */
    .message {{ margin-bottom: 20px; display: flex; align-items: flex-start; }}
    .avatar {{ width: 32px; height: 32px; border-radius: 50%; background-color: {PRIMARY_COLOR}; color: white; font-weight: bold; display: flex; align-items: center; justify-content: center; margin-right: 10px; flex-shrink: 0; font-size: 16px; }}
    .msg-text {{ padding: 10px 14px; background-color: white; border: 1px solid #ddd; border-radius: 18px; max-width: 75%; font-size: 15px; line-height: 1.5; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
    .user-msg {{ flex-direction: row-reverse; justify-content: flex-start; }}
    .user-msg .msg-text {{ background-color: #e6f2ff; text-align: left; border-color: #007bff33; }}
    .user-msg .avatar {{ background-color: #6c757d; margin-left: 10px; margin-right: 0; }}

    /* 4. CSS Cho Input Area Cố định */
    .stForm {{ flex-shrink: 0; padding: 10px 24px 10px 24px !important; margin-top: 0px; border-top: 1px solid #ddd; background-color: white; }}
    .stTextInput label {{ display: none; }}
    div[data-testid="stColumn"] {{ display: flex; align-items: center; gap: 10px; }}
    .stTextInput input {{ height: 50px; border-radius: 8px; border: 1px solid #ddd; box-shadow: 0 1px 3px rgba(0,0,0,0.05); padding: 10px 15px; }}
    [data-testid="stForm"] button {{ background-color: {PRIMARY_COLOR}; color: white; height: 50px; padding: 0 16px; font-size: 1rem; border-radius: 8px; }}


    /* CSS Input HỘP TRUNG TÂM & GỢI Ý */
    .suggestion-box {{ 
        background-color: white; 
        padding: 40px 30px; 
        border-radius: 16px; 
        box-shadow: 0 5px 15px rgba(0,0,0,0.1); 
        margin-top: 10vh; 
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
        text-align: center;
    }}
    .suggestion-box h3 {{ color: {PRIMARY_COLOR}; margin-bottom: 10px; font-size: 2rem; font-weight: 700; }}
    .suggestion-box p {{ color: #6c757d; margin-bottom: 30px; }}

    /* Các nút gợi ý LỚN (Làm nổi bật) */
    .suggestion-buttons-container {{ 
        display: flex; 
        flex-wrap: wrap; 
        justify-content: center; 
        gap: 15px; 
        margin-top: 20px;
        margin-bottom: 30px; /* Thêm margin dưới để cách Input */
    }}
    .suggestion-item {{ flex: 1 1 calc(50% - 30px); max-width: 350px; min-width: 250px; }}
    .suggestion-item button {{ 
        background-color: #f1f3f5; 
        border: 1px solid #dee2e6; 
        color: #333; 
        padding: 15px 20px; /* Kích thước lớn */
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 500;
        transition: 0.2s;
        width: 100%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    .suggestion-item button:hover {{ 
        background-color: #e9ecef;
        color: {PRIMARY_COLOR};
        border-color: {PRIMARY_COLOR}; 
        transform: translateY(-1px);
    }}

    /* Input box trung tâm (nhỏ gọn, nằm dưới) */
    .initial-input-container {{ margin-top: 20px; }}
    .initial-input-container .stTextInput input {{
        height: 50px; /* Nhỏ gọn hơn */
        font-size: 1rem; 
        border: 1px solid #ddd; /* Trở lại màu chuẩn */
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}

    </style>
""", unsafe_allow_html=True)

# ======= Layout chính: SỬ DỤNG st.sidebar CHO THANH BÊN =======

# Sidebar
with st.sidebar:
    # Nút Chat mới
    if st.button("＋ Chat mới", key="new_chat_btn"):
        st.session_state.messages = []
        st.session_state.input_key += 1
        st.rerun()

# Khu vực Chat Area Chính
st.markdown('<div class="chat-box" id="chatBox">', unsafe_allow_html=True)

# --- Logic hiển thị Gợi ý HOẶC Tin nhắn ---
if not st.session_state.messages:
    # HIỂN THỊ HỘP TRUNG TÂM
    st.markdown(f"""
        <div class="suggestion-box">
            <h3>Trợ lý ảo 👋🤖</h3>
            <p>Chào bạn! Bạn cần hỗ trợ gì hôm nay?</p>
    """, unsafe_allow_html=True)

    st.markdown('<div class="suggestion-buttons-container">', unsafe_allow_html=True)

    # 1. CÁC NÚT GỢI Ý (ĐẶT LÊN TRÊN)
    with st.container():
        cols = st.columns(2)
        for i, prompt in enumerate(SUGGESTION_PROMPTS):
            with cols[i % 2]:
                st.markdown('<div class="suggestion-item">', unsafe_allow_html=True)
                st.button(prompt, on_click=on_suggest_click, args=(prompt,), key=f"suggest_{i}")
                st.markdown('</div>', unsafe_allow_html=True)

    # st.markdown("""
    #         </div>
    #
    #         <div class="initial-input-container">
    # """, unsafe_allow_html=True)

    # 2. KHUNG INPUT TRUNG TÂM (ĐẶT XUỐNG DƯỚI)
    st.text_input(
        "Nhập câu hỏi của bạn:",
        value="",
        placeholder="Hoặc nhập câu hỏi của bạn tại đây...",
        key="initial_input_box",
        # Khi nhấn Enter, hàm handle_prompt sẽ được gọi
        on_change=lambda: handle_prompt(st.session_state.initial_input_box)
    )

    st.markdown("""
            </div> 
        </div>
    """, unsafe_allow_html=True)

else:
    # HIỂN THỊ TIN NHẮN (Giữ nguyên)
    for sender, msg in st.session_state.messages:
        if sender == "user":
            st.markdown(f"""
            <div class="message user-msg">
                <div class="avatar">👤</div>
                <div class="msg-text">{msg}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message">
                <div class="avatar">🤖</div>
                <div class="msg-text">{msg}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# # Vùng nhập liệu CỐ ĐỊNH (Chỉ hiển thị khi chat đã bắt đầu)
if st.session_state.messages:
    with st.container():
        with st.form("chat_form", clear_on_submit=True):
            col_input, col_button = st.columns([10, 1])

            with col_input:
                # st.text_input cho phép GỬI BẰNG ENTER
                user_input = st.text_input("Nhập tin nhắn của bạn:", value="",
                                           key=f"input_area_{st.session_state.input_key}")

            with col_button:
                send = st.form_submit_button("Gửi")

    # Logic xử lý gửi tin nhắn (Giữ nguyên)
    if send and st.session_state[f"input_area_{st.session_state.input_key}"].strip():
        handle_prompt(st.session_state[f"input_area_{st.session_state.input_key}"])