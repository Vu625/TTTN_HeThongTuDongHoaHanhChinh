def submit_application():
    pass
def get_application_status():
    pass
#logic gán cán bộ.

import streamlit as st
from services.ocr_service import extract_text, ocr_cccd
from pathlib import Path

# ========== Các hành động khả dụng ==========

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

        st.image(str(path), caption=path.name, width=350)
        if st.button(f"Chạy OCR cho {path.name}", key=path.name):
            text = ocr_cccd(path)
            app["ocr_texts"][path.name] = text["data"]
            st.success(f"✅ Đã trích xuất nội dung từ {path.name}")
            st.text_area(f"Nội dung OCR ({path.name})", text["data"] , height=150)
            if text["has_title"]:
                st.success("Căn Cước Công Dân" )
            else:
                st.error("Không Phải CCCD")
    return app

def approve_result(app):
    st.success("✅ Hồ sơ đã được phê duyệt!")
    app["status"] = "approved"
    return app

# ========== Bộ ánh xạ hàm ==========
ACTIONS = {
    "receive_application": receive_application,
    "extract_text": extract_text_action,
    "approve_result": approve_result,
}
