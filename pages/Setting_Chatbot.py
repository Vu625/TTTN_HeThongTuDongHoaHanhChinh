import os
import streamlit as st
from services.ocr_service import read_text_from_pdf
from services.rag_engine import bulk_prepare_and_index
import time
from services.layout import display_back_button
from services.auth_service import check_role
check_role("officer","admin")
# - Bật/tắt cache AI
FOLDER_PATH = 'data/db/law_texts'
# --- CẤU HÌNH ---
if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)
display_back_button()
st.title("📂 Cài Đặt cho ChatBot")

# Khởi tạo session state
if 'edit_file' not in st.session_state: st.session_state.edit_file = None
if 'view_file' not in st.session_state: st.session_state.view_file = None
if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0
# --- PHẦN 1: UPLOAD FILE (TXT HOẶC PDF) ---
st.subheader("1. Thêm tài liệu mới")
# Cho phép nhận cả txt và pdf
uploaded_file = st.file_uploader(
    "Chọn file .txt hoặc .pdf",
    type=['txt', 'pdf'],
    label_visibility="collapsed",
    key=f"uploader_{st.session_state.uploader_key}" # Key thay đổi -> Widget reset
)

if uploaded_file is not None:
    file_ext = uploaded_file.name.split('.')[-1].lower()

    # --- XỬ LÝ PDF ---
    if file_ext == 'pdf':
        temp_pdf_path = os.path.join(FOLDER_PATH, uploaded_file.name)
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner('Đang chạy OCR... (Vui lòng không tắt trình duyệt) ⏳'):
            result = read_text_from_pdf(temp_pdf_path)

        if result["status"] == "SUCCESS":
            txt_filename = uploaded_file.name.rsplit('.', 1)[0] + ".txt"
            txt_save_path = os.path.join(FOLDER_PATH, txt_filename)
            full_content = "\n\n".join(result["text_by_page"])

            with open(txt_save_path, "w", encoding="utf-8") as f:
                f.write(full_content)

            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

            # THÔNG BÁO VÀ RESET
            st.toast(f"✅ Đã OCR thành công {result['pages_count']} trang!", icon="🎉")

            # Tăng key lên 1 đơn vị để lần rerun tới, uploader sẽ mới tinh (trống rỗng)
            st.session_state.uploader_key += 1
            time.sleep(1)
            st.rerun()

        else:
            st.error(result["message"])
            if os.path.exists(temp_pdf_path): os.remove(temp_pdf_path)

    # --- XỬ LÝ TXT ---
    else:
        save_path = os.path.join(FOLDER_PATH, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.toast(f"✅ Đã thêm file text: {uploaded_file.name}", icon="floppy_disk")

        # Cũng reset key sau khi upload txt xong
        st.session_state.uploader_key += 1
        time.sleep(0.5)
        st.rerun()

st.markdown("---")

# --- PHẦN 2: DANH SÁCH & CHỨC NĂNG ---
st.subheader("2. Danh sách tài liệu hiện có")

files = [f for f in os.listdir(FOLDER_PATH) if f.endswith('.txt')]

if not files:
    st.info("Chưa có file nào.")
else:
    for file_name in files:
        file_path = os.path.join(FOLDER_PATH, file_name)

        # Chia cột: Tên (5 phần) | Xem (1.5 phần) | Sửa (1.5 phần) | Xóa (2 phần)
        col1, col2, col3, col4 = st.columns([5, 1.5, 1.5, 2])

        with col1:
            st.text(f"📄 {file_name}")

        with col2:
            # NÚT XEM (Toggle: Bấm để hiện/ẩn)
            if st.button("Xem", key=f"view_{file_name}"):
                # Nếu đang xem file này thì đóng lại (gán None), chưa thì mở ra
                if st.session_state.get('view_file') == file_name:
                    st.session_state.view_file = None
                else:
                    st.session_state.view_file = file_name
                    st.session_state.edit_file = None  # Tắt chế độ sửa nếu đang mở

        with col3:
            # NÚT SỬA
            if st.button("Sửa", key=f"edit_{file_name}"):
                # Nếu đang sửa file này thì đóng lại, chưa thì mở ra
                if st.session_state.edit_file == file_name:
                    st.session_state.edit_file = None
                else:
                    st.session_state.edit_file = file_name
                    st.session_state.view_file = None  # Tắt chế độ xem nếu đang mở

        with col4:
            # NÚT XÓA
            if st.button("Xóa ❌", key=f"del_{file_name}"):
                os.remove(file_path)
                # Reset lại trạng thái để tránh lỗi
                if st.session_state.edit_file == file_name: st.session_state.edit_file = None
                if st.session_state.get('view_file') == file_name: st.session_state.view_file = None
                st.toast(f"Đã xóa {file_name}")
                import time

                time.sleep(0.5)
                st.rerun()

        # --- KHU VỰC HIỂN THỊ NỘI DUNG (XEM HOẶC SỬA) ---

        # 1. Logic hiển thị khung XEM
        if st.session_state.get('view_file') == file_name:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            st.info(f"Nội dung file: {file_name}")
            st.code(content, language='text')  # Dùng st.code nhìn cho đẹp

        # 2. Logic hiển thị khung SỬA
        if st.session_state.edit_file == file_name:
            st.warning(f"✏️ Đang sửa: {file_name}")

            # Đọc nội dung hiện tại để đưa vào ô nhập liệu
            with open(file_path, "r", encoding="utf-8") as f:
                current_content = f.read()

            # Tạo Form để khi bấm Lưu mới submit
            with st.form(key=f"form_{file_name}"):
                new_content = st.text_area("Nội dung:", value=current_content, height=200)

                # Chia nút Lưu và Hủy
                c1, c2 = st.columns([1, 5])
                with c1:
                    submit_save = st.form_submit_button("💾 Lưu")

                if submit_save:
                    # Ghi đè nội dung mới vào file
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    st.success("Đã cập nhật thành công!")
                    st.session_state.edit_file = None  # Tắt chế độ sửa sau khi lưu
                    st.rerun()  # Load lại trang

if st.button("Áp Dụng Cho ChatBot"):
    bulk_prepare_and_index("data/db/law_texts")
    st.success("Đã Áp dụng thành công!, bây giờ Chatbot có thể các câu hỏi liên quan dến tài liệu phía trên")