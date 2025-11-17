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
import re
from  models.ocr.tessdata import config
# from models.ocr.tessdata import config
# tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# if tesseract_path:
#     pytesseract.tesseract_cmd = tesseract_path

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




# tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# if tesseract_path:
#     pytesseract.tesseract_cmd = tesseract_path



# 2. Thiết lập đường dẫn đến file ảnh CCCD bạn muốn OCR:
#    (Thay thế bằng đường dẫn tuyệt đối hoặc tương đối đến ảnh của bạn)
# img_path = "Cancuoc_vu.png"
# =========================================================================

def ocr_cccd(image_path):
    # Kiểm tra file ảnh có tồn tại không
    if not os.path.exists(image_path):
        print(f"❌ Lỗi: Không tìm thấy file ảnh tại đường dẫn: {image_path}")
        return {"data": {}, "has_title": False, "is_cccd_document": False}

    # Bước 1 & 2: Đọc ảnh (thay thế bước upload của Colab)
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"❌ Lỗi khi mở ảnh: {e}")
        return {"data": {}, "has_title": False, "is_cccd_document": False}

    # OCR 1: Grayscale để lấy chính xác "CĂN CƯỚC CÔNG DÂN"
    img_gray = image.convert("L")

    # ⚠️ Lưu ý: Trong PyCharm, không cần phải lưu file tạm trong /content/
    #           như Colab, nhưng ta vẫn giữ lại để dễ debug
    # img_gray.save("img_gray_temp.png")

    text_gray = pytesseract.image_to_string(img_gray, lang='vie')
    print("OCR Grayscale (cho title):")
    print(text_gray)

    # OCR 2: Ảnh gốc để lấy thông tin chi tiết chính xác
    text_original = pytesseract.image_to_string(image, lang='vie')
    print("\nOCR Original (cho data):")
    print(text_original)

    # Bước 3: Kiểm tra title từ OCR grayscale
    target_title = "CĂN CƯỚC CÔNG DÂN"
    has_title = target_title.lower() in text_gray.lower()
    print(f"\nCó 'CĂN CƯỚC CÔNG DÂN': {'✅ Đúng' if has_title else '❌ Sai'}")

    # --- BƯỚC 4: TÁCH THÔNG TIN BẰNG REGEX (GIỮ NGUYÊN CODE CỦA BẠN) ---
    data = {}

    # Số CCCD: Tìm chuỗi gần "số" hoặc 12 chữ số
    m = re.search(r'(?:số|só|xó|so)[/:\s]*([^\s]*\d{12}[^\s]*)', text_original, re.IGNORECASE)
    if not m:
        m = re.search(r'(\d{12})', text_original)
    if m:
        digits = re.sub(r'\D', '', m.group(1))
        if len(digits) >= 12:
            data['So_CCCD'] = digits[:12]

    # Họ và tên (mới) — tìm nội dung trên cùng dòng hoặc trên dòng tiếp theo nếu cùng dòng rỗng/không phải tên
    lines = text_original.splitlines()
    name_found = None
    for i, line in enumerate(lines):
        if re.search(r'Họ\s+và\s+tên', line, re.IGNORECASE):
            # kiểm tra cùng dòng
            after = re.sub(r'.*Họ\s+và\s+tên[^\w]*(.*)', r'\1', line, flags=re.IGNORECASE).strip()
            if after and not re.search(r'full\s*name', after, re.IGNORECASE):
                name_found = re.sub(r'^(Full\s*name[:\s\-]*)', '', after, flags=re.IGNORECASE).strip()
            else:
                # thử dòng tiếp theo (và tiếp theo nếu gặp dòng rỗng)
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines):
                    candidate = lines[j].strip()
                    # loại bỏ nếu candidate vẫn là label tiếng Anh
                    if not re.search(r'full\s*name', candidate, re.IGNORECASE):
                        name_found = candidate
            break

    if name_found:
        data['Ho_va_ten'] = name_found


    # Ngày sinh
    # Ngày sinh (phương án A mở rộng)
    m = re.search(r'Ngày\s*sinh[^\n\r]*?(\d{1,2}[/\\\-]\d{1,2}[/\\\-]\d{2,4})', text_original, re.IGNORECASE)
    birth_candidate = None
    if m:
        birth_candidate = m.group(1).strip()
    else:
        # nếu không có trong cùng dòng, thử lấy dòng kế tiếp
        pos = re.search(r'Ngày\s*sinh', text_original, re.IGNORECASE)
        if pos:
            rest = text_original[pos.end():].lstrip('\r\n')
            next_line = None
            for line in rest.splitlines():
                if line.strip():
                    next_line = line.strip()
                    break
            if next_line:
                m2 = re.search(r'(\d{1,2}[/\\\-]\d{1,2}[/\\\-]\d{2,4})', next_line)
                if m2:
                    birth_candidate = m2.group(1).strip()
    if birth_candidate:
        data['Ngay_sinh'] = birth_candidate

    # 🧩 Giới tính (mới thêm)
    gender_match = re.search(r'Giới\s*tính[^\n\r:]*[:\-]?\s*([A-Za-zÀ-Ỹà-ỹ]+)', text_original, re.IGNORECASE)
    gender_candidate = None
    if gender_match:
        gender_candidate = gender_match.group(1).strip()
    else:
        # nếu không có trong cùng dòng, tìm dòng kế tiếp
        pos = re.search(r'Giới\s*tính', text_original, re.IGNORECASE)
        if pos:
            rest = text_original[pos.end():].lstrip('\r\n')
            for line in rest.splitlines():
                if line.strip():
                    gender_candidate = line.strip().split()[0]
                    break
    if gender_candidate:
        # chuẩn hóa kết quả
        gender_candidate = gender_candidate.replace("quéc", "").replace("tịch", "").strip(" .:-")
        if re.search(r'nam', gender_candidate, re.IGNORECASE):
            data['Gioi_tinh'] = "Nam"
        elif re.search(r'nữ|nu|fem', gender_candidate, re.IGNORECASE):
            data['Gioi_tinh'] = "Nữ"
        else:
            data['Gioi_tinh'] = gender_candidate

    # Quê quán
    # ✅ Quê quán (đã chỉnh để lấy dòng kế tiếp nếu cần)
    lines = text_original.splitlines()
    for i, line in enumerate(lines):
        if re.search(r'Quê\s+quán', line, re.IGNORECASE):
            after = re.sub(r'.*Quê\s+quán[^\w]*(.*)', r'\1', line, flags=re.IGNORECASE).strip()
            if after and not re.search(r'Place\s*of\s*origin', after, re.IGNORECASE):
                data['Que_quan'] = after
            else:
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines):
                    candidate = lines[j].strip()
                    if not re.search(r'Place\s*of\s*origin', candidate, re.IGNORECASE):
                        data['Que_quan'] = candidate
            break


    # Nơi thường trú
    # Nơi thường trú — ưu tiên từ ảnh gốc, fallback sang ảnh grayscale nếu cần
    def extract_residence(text):
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if re.search(r'Nơi\s+thường\s+trú', line, re.IGNORECASE):
                after = re.sub(r'.*Nơi\s+thường\s+trú[^\w]*(.*)', r'\1', line, flags=re.IGNORECASE).strip()
                if after and not re.search(r'Place\s*of\s*residence', after, re.IGNORECASE):
                    return after
                else:
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines):
                        candidate = lines[j].strip()
                        if not re.search(r'Place\s*of\s*residence', candidate, re.IGNORECASE):
                            return candidate
        return None

    # Thử lấy từ ảnh gốc
    residence = extract_residence(text_original)

    # Nếu không có hoặc bị lỗi, thử lấy từ ảnh grayscale
    if not residence or len(residence) < 10:
        residence_gray = extract_residence(text_gray)
        if residence_gray and len(residence_gray) > len(residence or ''):
            residence = residence_gray

    if residence:
        data['Noi_thuong_tru'] = residence

    # --- KẾT THÚC BƯỚC 4 ---

    # Bước 5: Kiểm tra hợp lệ
    id_num = data.get('So_CCCD', '') # Sửa khóa từ 'Số CCCD' thành 'So_CCCD' cho nhất quán
    text_upper = (text_original + text_gray).upper()

    # Từ khóa nhận dạng CCCD
    required_keywords = ["CCCD", "CĂN CƯỚC CÔNG DÂN", "CIFIZEN LIDENTITY", "CITIZEN IDENTITY"]
    is_cccd_document = has_title or any(keyword in text_upper for keyword in required_keywords)

    # Từ khóa loại trừ
    forbidden_keywords = [
        "GIẤY PHÉP LÁI XE", "BẰNG LÁI XE", "DRIVER", "GTVT", "BỘ GTVT",
        "PASSPORT", "HỘ CHIẾU", "GIẤY PHÉP", "BẰNG", "XE MÁY", "Ô TÔ"
    ]
    is_forbidden_document = any(keyword in text_upper for keyword in forbidden_keywords)

    # Hợp lệ: Có title VÀ số 12 chữ số VÀ không forbidden
    if id_num and len(id_num) == 12 and has_title and not is_forbidden_document:
        print("\n✅ Thông tin căn cước công dân hợp lệ:")
        for k, v in data.items():
            print(f"{k}: {v}")
    elif id_num and len(id_num) == 12 and not has_title:
        print("\n❌ Ảnh có 12 chữ số, nhưng KHÔNG có 'CĂN CƯỚC CÔNG DÂN' → Không phải căn cước!")
    elif not id_num:
        print("\n❌ Lỗi: Không tìm thấy số CCCD 12 chữ số.")
    elif is_forbidden_document:
        print("\n❌ Lỗi: Có vẻ là tài liệu KHÔNG phải CCCD (Bằng lái/Passport...)")
    else:
        print("\n❌ Lỗi: Không thể xác nhận là Căn cước công dân.")

    # Trả về toàn bộ dữ liệu để có thể xử lý tiếp
    if 'So_CCCD' not in data:
        data['So_CCCD']=""
    if 'Ho_va_ten' not in data:
        data['Ho_va_ten']=""
    if 'Gioi_tinh' not in data:
        data['Gioi_tinh']=""
    if 'Que_quan' not in data:
        data['Que_quan']=""
    if 'Noi_thuong_tru' not in data:
        data['Noi_thuong_tru']=""
    data_ocr = [
        {'name':"So_CCCD",'label':"Số Căn Cước Công Dân",'text': data['So_CCCD']},
        {'name': "Ho_va_ten", 'label': "Họ Và Tên", 'text': data['Ho_va_ten']},
        {'name': "Gioi_tinh", 'label': "Giới Tính", 'text': data['Gioi_tinh']},
        {'name': "Que_quan", 'label': "Quê Quán", 'text': data['Que_quan']},
        {'name': "Noi_thuong_tru", 'label': "Nơi Thường Trú", 'text': data['Noi_thuong_tru']},
         ]
    return {
        "data": data_ocr,
        "has_title": has_title,

    }

# a = ocr_cccd("data\\db\\uploads\\GPLX_mattruoc.jpg")
#
# print(a)

