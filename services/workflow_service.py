def submit_application():
    pass
def get_application_status():
    pass
#logic gán cán bộ.

import streamlit as st
from services.ocr_service import extract_text, ocr_cccd
from pathlib import Path
from services.data_viz_service import save_applications

# ========== Các hành động khả dụng ==========
import streamlit as st
# Khởi tạo trạng thái nếu chưa tồn tại
if 'ocr_data_raw' not in st.session_state:
    st.session_state.ocr_data_raw = None
if 'ocr_key' not in st.session_state:
    st.session_state.ocr_key = None # Dùng để kiểm tra file nào đang được hiển thị

def basic_check(app):
    st.subheader("📝 Kiểm tra thông tin hồ sơ (Basic Check)")

    st.markdown("### 📌 Thông tin công dân đã gửi:")
    st.json(app.get("form_data", {}))

    st.divider()
    st.markdown("### 📎 Tài liệu đính kèm:")
    for doc in app.get("documents", []):
        st.write(f"• {doc}")

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

        st.success("Đã ghi nhận lý do từ chối.")

        return app

    # NÚT XONG
    if st.button("Xong"):
        st.success("Hoàn tất. Công dân sẽ nhận thông báo.")

    return app

def receive_application(app):
    st.info("📥 Hồ sơ đã được tiếp nhận. Không có hành động tự động.")
    return app

def extract_text_action(app):
    st.subheader("🔍 OCR - Trích xuất thông tin từ ảnh")
    if "documents" not in app or not app["documents"]:
        st.warning("Không có file để chạy OCR.")
        return app

    if "ocr_texts" not in app:
        app["ocr_texts"] = {}

    for doc_path in app["documents"]:
        path = Path(doc_path)
        if not path.exists():
            st.error(f"Không tìm thấy file: {path}")
            continue

        # st.image(str(path), caption=path.name, width=350)
        # if st.button(f"Chạy OCR cho {path.name}", key=path.name):
        #     text = ocr_cccd(path)
        #     st.success(f"✅ Đã trích xuất nội dung từ {path.name}")
        #     st.text_area(f"Nội dung OCR ({path.name})", text["data"] , height=150)
        #     text_fix={}
        #     for field in text["data"]:
        #         text_fix[field["name"]] = st.text_input(label=field["label"], value=field["text"],key=field["name"])
        #         text_fix[field["name"]] = st.session_state[field["name"]]
        #     if st.button("Lưu Nội Dung Quét OCR"):
        #         app["ocr_texts"] = text_fix
        #     if text["has_title"]:
        #         st.success("Căn Cước Công Dân" )
        #     else:
        #         st.error("Không Phải CCCD")
        st.image(str(path), caption=path.name, width=350)

        # Logic KÍCH HOẠT OCR (Chỉ lưu kết quả vào state)
        if st.button(f"Chạy OCR cho {path.name}", key=path.name):
            text = ocr_cccd(path)
            st.session_state.ocr_data_raw = text["data"]  # Lưu kết quả OCR vào state
            st.session_state.ocr_key = path.name  # Lưu key file đang được OCR
            st.success(f"✅ Đã trích xuất nội dung từ {path.name}")

        # Logic HIỂN THỊ INPUT (Luôn chạy, chỉ kiểm tra state)
        # Chỉ hiển thị các ô input nếu có dữ liệu OCR cho file hiện tại
        if st.session_state.ocr_data_raw and st.session_state.ocr_key == path.name:

            # 1. Hiển thị Text Area (Tùy chọn)
            st.text_area(f"Nội dung OCR ({path.name})", str(st.session_state.ocr_data_raw), height=150)

            # 2. Tạo các ô Input Sửa lỗi (Luôn render khi có dữ liệu)
            st.markdown("---")
            st.subheader("📝 Sửa lỗi Trích xuất")

            text_fix = {}
            for field in st.session_state.ocr_data_raw:
                # Tạo key duy nhất cho ô input
                input_key = f"input_{st.session_state.ocr_key}_{field['name']}"

                # st.text_input được gọi. Streamlit tự động duy trì giá trị qua session_state[input_key]
                st.text_input(
                    label=field["label"],
                    value=field["text"],
                    key=input_key  # Key duy nhất bắt buộc
                )

                # Lấy giá trị hiện tại (đã sửa hoặc gốc)
                text_fix[field["name"]] = st.session_state[input_key]

            # 3. Nút Lưu (Áp dụng các giá trị đã sửa)
            if st.button("Lưu Nội Dung Quét OCR", key=f"save_btn_{path.name}"):
                app["ocr_texts"][path.name] = text_fix
                st.success(f"💾 Đã lưu nội dung đã sửa cho {path.name}")

            # Xóa trạng thái nếu cần chuyển sang file khác
            # ...
    return app

# def approve_result(app):
#     st.success("✅ Hồ sơ đã được phê duyệt!")
#     app["status"] = "approved"
#     return app
def approve_result(app):
    st.subheader("🎉 Phê duyệt kết quả hồ sơ")

    st.markdown("### ✔️ Hồ sơ đủ điều kiện phê duyệt")
    st.info("Bạn có thể thêm ghi chú gửi cho Công dân (tùy chọn).")

    note = st.text_area(
        "Ghi chú gửi cho công dân (không bắt buộc):",
        value=app.get("approve_note", ""),
        placeholder="Ví dụ: Vui lòng đến Cục Cảnh Sát để nhận giấy tờ liên quan.",
        key="approve_note_input"
    )

    if st.button("📤 Xác nhận phê duyệt", key="approve_submit"):
        app["status"] = "approved"
        app["approve_result"] = "success"
        app["approve_note"] = note
        st.success("Hồ sơ đã được phê duyệt thành công!")
        return app

    return app

# ========== Bộ ánh xạ hàm ==========
ACTIONS = {
    "basic_check": basic_check,
    "extract_text": extract_text_action,
    "approve_result": approve_result,
}
