def run_ocr_and_validate():
    #(tích hợp Tesseract, PIL, RegEx).
    pass
import numpy as np
import cv2
import pytesseract
from PIL import Image
from pathlib import Path
import io
import streamlit as st
import os
from models.ocr.tessdata import config

UPLOAD_DIR = Path("data/db/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def save_uploaded_file(uploaded_file):
    file_path = UPLOAD_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(file_path)

# def extract_text(file_path):
#     try:
#         img = Image.open(file_path)
#         text = pytesseract.image_to_string(img, lang="vie")
#         return text.strip()
#     except Exception as e:
#         st.error(f"Lỗi OCR: {e}")
#         return ""

def preprocess_image(image_path):
    """
    Tiền xử lý hình ảnh: Chuyển sang thang độ xám, làm mờ và phân ngưỡng thích nghi.
    Mục đích: Giúp Tesseract dễ dàng phân biệt chữ cái và nền.
    """
    try:
        # 1. Tải ảnh bằng OpenCV (dễ xử lý hơn PIL cho các bước nâng cao)
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError("Không thể đọc file ảnh.")

        # 2. Chuyển ảnh sang thang độ xám (Grayscale)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 3. Làm mờ Gaussian: Giúp loại bỏ nhiễu và làm mịn các chi tiết nhỏ
        # gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # 4. Phân ngưỡng thích nghi (Adaptive Thresholding):
        # Biến đổi ảnh thành trắng đen dựa trên cường độ sáng cục bộ.
        # Rất hiệu quả với ảnh có điều kiện ánh sáng không đều (như ảnh chụp).
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Thử nghiệm thêm: Nếu font chữ nhỏ hoặc bị mờ, có thể cần Dilation/Erosion
        # kernel = np.ones((1, 1), np.uint8)
        # thresh = cv2.erode(thresh, kernel, iterations=1)
        # thresh = cv2.dilate(thresh, kernel, iterations=1)

        # Chuyển đổi ảnh OpenCV (numpy array) sang định dạng PIL Image
        # để tương thích với pytesseract.image_to_string
        return Image.fromarray(gray)

    except Exception as e:
        st.error(f"Lỗi tiền xử lý ảnh: {e}")
        return None


def extract_text(file_path):
    """
    Trích xuất văn bản từ file ảnh sau khi đã tiền xử lý.
    """
    # 1. Tiền xử lý ảnh
    processed_img = preprocess_image(file_path)

    if processed_img is None:
        return ""

    try:
        # 2. Gọi OCR trên ảnh đã xử lý
        # lang="vie" chỉ định gói ngôn ngữ Tiếng Việt
        # --psm 6: Giả định một khối văn bản duy nhất (Thích hợp cho giấy tờ)
        custom_config = r'--psm 6'

        text = pytesseract.image_to_string(processed_img, lang="vie", config=custom_config)

        return text.strip()

    except Exception as e:
        # Hiển thị lỗi cuối cùng (có thể là lỗi ngôn ngữ, hoặc file không đọc được)
        st.error(f"Lỗi OCR: Không thể trích xuất văn bản. Chi tiết: {e}")
        return ""