def submit_application():
    pass
def get_application_status():
    pass
#logic gán cán bộ.
import streamlit as st
from services.ocr_service import extract_text, read_text_from_pdf , send_cccd_file, send_gplx_file
from pathlib import Path
import datetime
import base64
from services.data_viz_service import save_applications

# ========== Các hành động khả dụng ==========
# Khởi tạo trạng thái nếu chưa tồn tại


def basic_check(app):
    st.subheader("📑 Kiểm tra thông tin hồ sơ")
    st.divider()

    st.markdown("### 📎 Tài liệu đính kèm:")
    # for doc in app.get("documents", []):
    #     st.write(f"• {doc}")
    #     st.image(str(doc), width=350)
    # st.divider()

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

            # Hiển thị ảnh
            if p.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                st.image(str(p), caption=p.name, width=350)

            elif p.suffix.lower() == ".pdf":
                st.markdown("#### 📑 Xem file PDF:")
                try:
                    # CÁCH 1: Dùng st.pdf (Yêu cầu Streamlit >= 1.32)
                    st.pdf(str(p))
                except:
                    # CÁCH 2: Fallback bằng iframe + base64 (Đáng tin cậy cho file cục bộ)
                    try:
                        with open(p, "rb") as f:
                            base64_pdf = base64.b64encode(f.read()).decode('utf-8')

                        pdf_display = f"""
                                        <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf">
                                        </iframe>
                                        """
                        st.markdown(pdf_display, unsafe_allow_html=True)
                    except Exception as e:
                        st.warning(f"Không thể nhúng PDF. Vui lòng cập nhật Streamlit. Chi tiết lỗi: {e}")

            else:
                st.info(f"Không thể xem trực tiếp file: {p.suffix}")

            # st.divider()

    st.markdown("### 📌 Các thông tin công dân đã điền:")
    for item in app['form_data']:
        st.markdown(f"##### 📝 {item['label']}")
        st.warning(item['content'])
    st.divider()

    # ==============================
    # KHỞI TẠO SESSION STATE
    # ==============================
    if "reject_mode" not in st.session_state:
        st.session_state.reject_mode = False
    if "reject_reason_selected" not in st.session_state:
        st.session_state.reject_reason_selected = None
    if "reject_other_text" not in st.session_state:
        st.session_state.reject_other_text = ""

    # ==============================
    # TRẠNG THÁI: CHƯA CHỌN GÌ
    # ==============================
    if not st.session_state.reject_mode:
        col1, col2 = st.columns(2)

        with col1:
            approve = st.button("✔️ Duyệt", key="approve_basic_check")

        with col2:
            reject = st.button("❌ Không duyệt", key="reject_basic_check")

        if approve:
            app["basic_check_result"] = "approved"
            st.success("Đã duyệt! Bạn có thể chuyển sang bước tiếp theo.")
            return app

        if reject:
            st.session_state.reject_mode = True
            st.rerun()

    # ==============================
    # TRẠNG THÁI: ĐANG Ở MÀN HÌNH TỪ CHỐI
    # ==============================
    if st.session_state.reject_mode :
        st.error("Hồ sơ không được duyệt. Vui lòng chọn lý do:")

    # LÝ DO TỪ CHỐI
        st.session_state.reject_reason_selected = st.radio(
        "Lý do từ chối:",
        ["Không đủ thông tin yêu cầu", "Nộp sai thông tin yêu cầu", "Lý do khác"],
        index=0 if st.session_state.reject_reason_selected is None else
        ["Không đủ thông tin yêu cầu", "Nộp sai thông tin yêu cầu", "Lý do khác"].index(st.session_state.reject_reason_selected),
        key="radio_reason"
        )

        if st.session_state.reject_reason_selected == "Lý do khác":
            st.session_state.reject_other_text = st.text_input(
            "Nhập lý do khác:",
            value=st.session_state.reject_other_text,
            key="other_reason_input"
        )

        if st.button("📤 Gửi lý do từ chối", key="confirm_reject"):
            final_reason = (
            st.session_state.reject_other_text
            if st.session_state.reject_reason_selected == "Lý do khác"
            else st.session_state.reject_reason_selected
        )

            app["basic_check_result"] = "rejected"
            app["reject_reason"] = final_reason
            app["status"] = "rejected"
            app["notification"] = {
            "seen": False,
            "type": "rejected",
            "message": final_reason,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.success("Đã ghi nhận lý do từ chối.")
            del st.session_state.reject_mode

        return app

    return app

def receive_application(app):
    st.info("📥 Hồ sơ đã được tiếp nhận. Không có hành động tự động.")
    return app

def extract_text_action_CCCD(app):
    st.subheader("🔍 OCR & Trích xuất văn bản từ tài liệu")
    st.divider()

    # Khởi tạo Session State nếu chưa có
    if 'ocr_data_raw' not in st.session_state:
        st.session_state.ocr_data_raw = None
    if 'current_file_key' not in st.session_state:
        st.session_state.current_file_key = None
    if 'action_type' not in st.session_state:
        st.session_state.action_type = None

    if "documents" not in app or not app["documents"]:
        st.warning("Không có file để chạy xử lý.")
        return app

    if "ocr_texts" not in app:
        app["ocr_texts"] = {}

    for doc_path in app["documents"]:
        path = Path(doc_path)
        file_key = str(path.name)

        st.markdown(f"### ➡️ {path.name}")

        if not path.exists():
            st.error(f"⚠️ File không tìm thấy: {path}")
            st.divider()
            continue

        is_image = path.suffix.lower() in [".png", ".jpg", ".jpeg"]
        is_pdf = path.suffix.lower() == ".pdf"

        # --- PHẦN 1: KÍCH HOẠT ACTION (OCR/READ PDF) ---

        # Xử lý Hình ảnh (Hiển thị ảnh và nút OCR)
        if is_image:
            st.image(str(path), caption=path.name, width=350)
            ocr_button_label = f"✨ Quét OCR cho **Hình ảnh**"

            if st.button(ocr_button_label, key=f"ocr_btn_{file_key}"):
                with st.spinner(f"Đang chạy OCR cho ảnh {path.name}..."):
                    raw_data = send_cccd_file(path)
                    st.session_state.ocr_data_raw = raw_data
                    st.session_state.current_file_key = file_key
                    st.session_state.action_type = "image_ocr"
                    st.success(f"✅ Đã trích xuất nội dung CCCD từ {path.name}")
                st.rerun()

        # Xử lý PDF (Không hiển thị ảnh, chỉ hiển thị thông báo và nút)
        elif is_pdf:
            st.info("File là PDF. Vui lòng nhấn nút để đọc nội dung văn bản.")
            ocr_button_label = f"📖 Quét văn bản cho **PDF**"

            if st.button(ocr_button_label, key=f"ocr_btn_{file_key}"):
                with st.spinner(f"Đang đọc văn bản từ PDF {path.name}..."):
                    raw_data = read_text_from_pdf(path)
                    st.session_state.ocr_data_raw = raw_data
                    st.session_state.current_file_key = file_key
                    st.session_state.action_type = "pdf_text"
                    st.success(f"✅ Đã đọc toàn bộ văn bản từ {path.name}")
                st.rerun()

        else:
            st.warning(f"Định dạng file {path.suffix} không được hỗ trợ để xử lý.")

        # --- PHẦN 2: HIỂN THỊ KẾT QUẢ VÀ SỬA LỖI ---

        # Chỉ hiển thị kết quả nếu file hiện tại trùng với file vừa được xử lý
        if st.session_state.current_file_key == file_key:
            st.markdown("---")

            # 2.1 Hiển thị và Sửa lỗi cho IMAGE OCR (CCCD - Dạng trường dữ liệu)
            if st.session_state.action_type == "image_ocr" and st.session_state.ocr_data_raw and "data" in st.session_state.ocr_data_raw:
                st.subheader("📝 Sửa lỗi Trích xuất CCCD (Hình ảnh)")

                text_fix = {}
                data_fields = st.session_state.ocr_data_raw.get("data", [])

                for field in data_fields:
                    input_key = f"input_fix_{file_key}_{field['name']}"

                    st.text_input(
                        label=field["label"],
                        value=field["text"],
                        key=input_key
                    )
                    text_fix[field["name"]] = st.session_state[input_key]

                # if st.button("💾 Lưu Nội Dung OCR Đã Sửa", key=f"save_ocr_btn_{file_key}"):
                app["ocr_texts"][file_key] = text_fix
                st.success(f"💾 Đã lưu nội dung CCCD {file_key}.")

            # 2.2 Hiển thị và Lưu kết quả READ TEXT từ PDF (Dạng khối văn bản)
            elif st.session_state.action_type == "pdf_text" and st.session_state.ocr_data_raw and "text_by_page" in st.session_state.ocr_data_raw:
                st.subheader("📖 Nội dung văn bản trích xuất từ PDF")

                all_text = ""
                text_by_page = st.session_state.ocr_data_raw["text_by_page"]

                # Gộp nội dung từ các trang
                for page_index, text in enumerate(text_by_page):
                    page_num = page_index + 1
                    all_text += f"\n\n=== Trang {page_num} ===\n"
                    all_text += text

                # Hiển thị text_area
                pdf_text_key = f"pdf_text_area_{file_key}"
                st.text_area(
                    "Toàn bộ văn bản trích xuất (Có thể kiểm tra và sửa lỗi)",
                    value=all_text.strip(),
                    height=400,
                    key=pdf_text_key
                )

                if st.button("💾 Lưu Nội Dung Text PDF", key=f"save_pdf_text_btn_{file_key}"):
                    # Lưu nội dung đã sửa/kiểm tra từ text_area
                    app["ocr_texts"][file_key] = {
                        "all_text": st.session_state[pdf_text_key],
                        "source_type": "PDF_Text"
                    }
                    st.success(f"💾 Đã lưu nội dung văn bản từ PDF cho {file_key}.")

            st.divider()

    return app

def approve_result(app):
    st.subheader("🎉 Phê duyệt kết quả hồ sơ")

    note = st.text_area(
        "Ghi chú gửi cho công dân:",
        value=app.get("approve_note", ""),
        placeholder="Ví dụ: Vui lòng đến Cục Cảnh Sát để nhận giấy tờ liên quan."
    )

    if st.button("📤 Xác nhận phê duyệt"):
        app["status"] = "approved"
        app["approve_result"] = "success"
        app["approve_note"] = note

        app["notification"] = {
            "seen": False,
            "type": "approved",
            "message": note,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        st.success("Hồ sơ đã được phê duyệt thành công!")
        return app

    return app

def extract_text_action_GPLX(app):
    st.subheader("🔍 OCR & Trích xuất văn bản từ tài liệu")
    st.divider()

    # --- KHỞI TẠO SESSION STATE ---
    # Dùng key riêng biệt để tránh xung đột
    if 'gplx_ocr_data_raw' not in st.session_state:
        st.session_state.gplx_ocr_data_raw = None
    if 'gplx_current_file_key' not in st.session_state:
        st.session_state.gplx_current_file_key = None
    if 'gplx_action_type' not in st.session_state:
        st.session_state.gplx_action_type = None

    if "documents" not in app or not app["documents"]:
        st.warning("Không có file để chạy xử lý.")
        return app

    if "ocr_texts" not in app:
        app["ocr_texts"] = {}

    for doc_path in app["documents"]:
        path = Path(doc_path)
        file_key = str(path.name)

        st.markdown(f"### ➡️ {path.name}")

        if not path.exists():
            st.error(f"⚠️ File không tìm thấy: {path}")
            st.divider()
            continue

        is_image = path.suffix.lower() in [".png", ".jpg", ".jpeg"]
        is_pdf = path.suffix.lower() == ".pdf"

        # --- PHẦN 1: KÍCH HOẠT ACTION (OCR/READ PDF) ---

        # Xử lý Hình ảnh (OCR cho GPLX)
        if is_image:
            # CHỈ GỌI st.image() CHO FILE HÌNH ẢNH
            st.image(str(path), caption=path.name, width=350)
            ocr_button_label = f"✨ Quét OCR cho **Hình ảnh** GPLX"

            if st.button(ocr_button_label, key=f"ocr_btn_{file_key}"):
                with st.spinner(f"Đang chạy OCR cho ảnh {path.name}..."):
                    raw_data = send_gplx_file(path)
                    st.session_state.gplx_ocr_data_raw = raw_data
                    st.session_state.gplx_current_file_key = file_key
                    st.session_state.gplx_action_type = "image_ocr"
                    st.success(f"✅ Đã trích xuất nội dung GPLX từ {path.name}")
                st.rerun()

        # Xử lý PDF (Đọc văn bản)
        elif is_pdf:
            st.info("File là PDF. Vui lòng nhấn nút để đọc nội dung văn bản.")
            ocr_button_label = f"📖 Quét văn bản cho **PDF**"

            if st.button(ocr_button_label, key=f"ocr_btn_{file_key}"):
                with st.spinner(f"Đang đọc văn bản từ PDF {path.name}..."):
                    raw_data = read_text_from_pdf(path)
                    st.session_state.gplx_ocr_data_raw = raw_data
                    st.session_state.gplx_current_file_key = file_key
                    st.session_state.gplx_action_type = "pdf_text"
                    st.success(f"✅ Đã đọc toàn bộ văn bản từ {path.name}")
                st.rerun()

        else:
            st.warning(f"Định dạng file {path.suffix} không được hỗ trợ để xử lý.")

        # --- PHẦN 2: HIỂN THỊ KẾT QUẢ VÀ SỬA LỖI ---

        # Chỉ hiển thị kết quả nếu file hiện tại trùng với file vừa được xử lý
        if st.session_state.gplx_current_file_key == file_key:
            st.markdown("---")

            # 2.1 Hiển thị và Sửa lỗi cho IMAGE OCR (GPLX - Dạng trường dữ liệu)
            if st.session_state.gplx_action_type == "image_ocr" and st.session_state.gplx_ocr_data_raw and "data" in st.session_state.gplx_ocr_data_raw:
                st.subheader("📝 Sửa lỗi Trích xuất GPLX (Hình ảnh)")

                text_fix = {}
                data_fields = st.session_state.gplx_ocr_data_raw.get("data", [])

                for field in data_fields:
                    input_key = f"input_fix_{file_key}_{field['name']}"

                    # st.text_input được gọi với key duy nhất
                    st.text_input(
                        label=field["label"],
                        value=field["text"],
                        key=input_key
                    )
                    text_fix[field["name"]] = st.session_state[input_key]

                # if st.button("💾 Lưu Nội Dung OCR Đã Sửa", key=f"save_ocr_btn_{file_key}"):
                app["ocr_texts"][file_key] = text_fix
                st.success(f"💾 Đã lưu nội dung GPLX đã sửa cho {file_key}.")

            # 2.2 Hiển thị và Lưu kết quả READ TEXT từ PDF (Dạng khối văn bản)
            elif st.session_state.gplx_action_type == "pdf_text" and st.session_state.gplx_ocr_data_raw and "text_by_page" in st.session_state.gplx_ocr_data_raw:
                st.subheader("📖 Nội dung văn bản trích xuất từ PDF")

                all_text = ""
                text_by_page = st.session_state.gplx_ocr_data_raw["text_by_page"]

                for page_index, text in enumerate(text_by_page):
                    page_num = page_index + 1
                    all_text += f"\n\n=== Trang {page_num} ===\n"
                    all_text += text

                pdf_text_key = f"pdf_text_area_{file_key}"
                st.text_area(
                    "Toàn bộ văn bản trích xuất (Có thể kiểm tra và sửa lỗi)",
                    value=all_text.strip(),
                    height=400,
                    key=pdf_text_key
                )

                if st.button("💾 Lưu Nội Dung Text PDF", key=f"save_pdf_text_btn_{file_key}"):
                    app["ocr_texts"][file_key] = {
                        "all_text": st.session_state[pdf_text_key],
                        "source_type": "PDF_Text"
                    }
                    st.success(f"💾 Đã lưu nội dung văn bản từ PDF cho {file_key}.")

            st.divider()

    return app

# ========== Bộ ánh xạ hàm ==========
ACTIONS = {
    "basic_check": basic_check,
    "extract_text_cccd": extract_text_action_CCCD,
    "extract_text_gplx": extract_text_action_GPLX,
    "approve_result": approve_result,
}
