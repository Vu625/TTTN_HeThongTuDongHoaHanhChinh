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
from typing import List, Dict
import fitz
import requests

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


def ocr_cccd(image_path):
    # Kiểm tra file ảnh có tồn tại không
    if not os.path.exists(image_path):
        print(f"❌ Lỗi: Không tìm thấy file ảnh tại đường dẫn: {image_path}")
        return {"data": {}, "has_title": False, "is_cccd_document": False}
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"❌ Lỗi khi mở ảnh: {e}")
        return {"data": {}, "has_title": False, "is_cccd_document": False}
    img_gray = image.convert("L")

    text_gray = pytesseract.image_to_string(img_gray, lang='vie')
    print("OCR Grayscale (cho title):")
    print(text_gray)

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

OCR_AVAILABLE = True
def read_text_from_pdf(pdf_path: str) -> Dict[str, any]:
    text_by_page = []
    try:
        # Kiểm tra sự tồn tại của file trước khi mở
        if not os.path.exists(pdf_path):
            return {
                "status": "ERROR",
                "message": f"Lỗi: Không tìm thấy file tại đường dẫn {pdf_path}",
                "pages_count": 0,
                "text_by_page": []
            }
        document = fitz.open(pdf_path)
        if len(document) == 0:
            document.close()
            return {
                "status": "ERROR",
                "message": "Lỗi: Tài liệu PDF trống, không có trang nào.",
                "pages_count": 0,
                "text_by_page": []
            }
        # Lặp qua từng trang
        for page_num in range(len(document)):
            page = document.load_page(page_num)

            # 1. THỬ TRÍCH XUẤT VĂN BẢN TRỰC TIẾP (PHƯƠNG PHÁP CHUẨN)
            text = page.get_text("text")

            # 2. KIỂM TRA NẾU VĂN BẢN TRỐNG VÀ OCR CÓ SẴN -> THỰC HIỆN OCR DỰ PHÒNG
            if not text.strip() and OCR_AVAILABLE:
                print(f"-> Trang {page_num + 1}: Không tìm thấy lớp văn bản. Đang chuyển sang dùng OCR...")
                try:
                    # Tăng độ phân giải lên 300 DPI để OCR chính xác hơn
                    zoom_matrix = fitz.Matrix(3, 3)
                    pix = page.get_pixmap(matrix=zoom_matrix)

                    # Chuyển Pixmap (PyMuPDF) sang đối tượng PIL Image
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                    # Thực hiện OCR, sử dụng ngôn ngữ Tiếng Việt ('vie') và Tiếng Anh ('eng')
                    text = pytesseract.image_to_string(img, lang='vie+eng')

                    if not text.strip():
                        text = "(Không trích xuất được văn bản nào bằng OCR)"

                except Exception as e:
                    text = f"(Lỗi OCR: {e}) - Vui lòng kiểm tra lại cấu hình Tesseract."

            elif not text.strip() and not OCR_AVAILABLE:
                text = "(Không tìm thấy lớp văn bản. Không thể dùng OCR vì thiếu thư viện.)"

            text_by_page.append(text)

        # Đóng tài liệu sau khi hoàn tất
        document.close()

        return {
            "status": "SUCCESS",
            "pages_count": len(text_by_page),
            "text_by_page": text_by_page
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Lỗi khi xử lý PDF: {e}",
            "pages_count": 0,
            "text_by_page": []
        }

def ocr_gplx(img_path):
    # Bước 1: Yêu cầu đường dẫn file ảnh cục bộ
    # print("📸 Vui lòng nhập đường dẫn tới ảnh Giấy phép lái xe cục bộ (ví dụ: C:\\Users\\...\\gplx.jpg):")
    # img_path = input("Đường dẫn file: ").strip()

    # Kiểm tra tính hợp lệ của đường dẫn file
    if not img_path or not os.path.exists(img_path):
        print(f"❌ Đường dẫn file không hợp lệ hoặc file không tồn tại: {img_path}")
        return None

    # Bước 2: Đọc ảnh
    try:
        image = Image.open(img_path)
    except Exception as e:
        print(f"❌ Lỗi khi mở ảnh: {e}")
        return None

    # OCR 1: Grayscale để lấy chính xác "GIẤY PHÉP LÁI XE"
    img_gray = image.convert("L")
    text_gray = pytesseract.image_to_string(img_gray, lang='vie')
    print("\n--- OCR Grayscale (cho title) ---")
    print(text_gray)

    # OCR 2: Ảnh gốc để lấy thông tin chi tiết chính xác
    text_original = pytesseract.image_to_string(image, lang='vie')
    print("\n--- OCR Original (cho data) ---")
    print(text_original)

    # Bước 3: Kiểm tra title từ OCR grayscale
    target_title_regex = r'GIẤY PHÉP LÃIXE'
    title_match = re.search(target_title_regex, text_gray, re.IGNORECASE)
    has_title_found = bool(title_match)
    print(f"\nCó 'GIẤY PHÉP LÁI XE': {'✅ Đúng' if has_title_found else '❌ Sai'}")

    # Bước 4: Tách thông tin (line-based parsing, an toàn hơn)
    data = {}
    text_combined = (text_original + "\n" + text_gray).strip()
    # Chuẩn hóa một chút: thay các ký tự lạ thường thấy
    normalized = text_combined.replace('Ð', 'Đ').replace('ð', 'đ').replace('', '')
    # Tách thành dòng, loại bỏ các dòng chỉ có ký tự lạ whitespace
    lines = [ln.strip() for ln in normalized.splitlines() if ln.strip()]

    # Helper: tìm giá trị sau label trong cùng dòng hoặc dòng kế tiếp
    def find_field(label_patterns):
        """
        label_patterns: list of regex patterns (case-insensitive) để nhận diện label trong 1 dòng
        Trả về giá trị (chuỗi) hoặc None.
        """
        for i, ln in enumerate(lines):
            for pat in label_patterns:
                if re.search(pat, ln, re.IGNORECASE):
                    # nếu có dấu ":" hoặc "No:" hoặc "/" thì tách phần sau
                    # tìm vị trí của ':' đầu tiên trong dòng
                    if ':' in ln:
                        after = ln.split(':', 1)[1].strip()
                        if after:
                            return after
                    # nếu không có ":" hoặc phần sau rỗng -> lấy dòng kế tiếp không rỗng
                    j = i + 1
                    while j < len(lines) and lines[j].strip() == '':
                        j += 1
                    if j < len(lines):
                        return lines[j].strip()
        return None

    # ===== Số GPLX (12 chữ số) =====
    # Tìm mẫu Số/No/So: 123456789012 (10+ chữ số)
    m = re.search(r'(?:số|só|so|sô|no)[/:\s]*([^\s]*\d{10,}\b)', normalized, re.IGNORECASE)
    if not m:
        # Tìm mẫu 12 chữ số đơn thuần
        m = re.search(r'(\d{12})', normalized)

    # Tiền xử lý để đảm bảo lấy đúng 12 chữ số
    digits = ''
    if m:
        digits = re.sub(r'\D', '', m.group(1))  # Chỉ giữ lại chữ số
        if len(digits) >= 12:
            data['So_GPLX'] = digits[:12]
        else:
            # Thử tìm lại 12 chữ số không cần prefix nếu mẫu đầu tiên bị lỗi (ví dụ OCR bỏ lỡ prefix)
            m_12 = re.search(r'(\d{12})', normalized)
            if m_12:
                data['So_GPLX'] = m_12.group(1)

    # ===== Họ và tên =====
    name_val = find_field([r'Họ\s*tên', r'Họ\s*và\s*tên', r'Full\s*name', r'Name'])
    if name_val:
        # loại bỏ nhãn tiếng Anh nếu dính
        name_val = re.sub(r'^(Full\s*name[:\s\-]*)', '', name_val, flags=re.IGNORECASE).strip()
        # nếu name_val chứa từ "Ngày" hoặc "Ngày sinh" thì tách bỏ phần đó (ngăn OCR nối nhãn)
        name_val = re.split(r'\bNgày\b|\bDate\b', name_val, flags=re.IGNORECASE)[0].strip()
        data['Ho_va_ten'] = name_val

    # ===== Ngày sinh (dd/mm/yyyy) =====
    birth_val = find_field([r'Ngày\s*sinh', r'Date\s*of\s*Birth', r'Date\s*of\s*Binh', r'DOB'])
    date_found = False

    if birth_val:
        # tìm dd/mm/yyyy trong birth_val
        m = re.search(r'([0-3]?\d[/\\\-][0-3]?\d[/\\\-]\d{4})', birth_val)
        if m:
            data['Ngay_sinh'] = m.group(1)
            date_found = True

    # Nếu vẫn chưa có ngày sinh, dò toàn văn bản sau label 'Ngày sinh' (nếu có)
    if not date_found:
        pos = re.search(r'Ngày\s*sinh|Date\s*of\s*Birth|Date\s*of\s*Binh', normalized, re.IGNORECASE)
        if pos:
            # lookahead ngắn sau label
            after = normalized[pos.end():pos.end() + 60]
            m_after = re.search(r'([0-3]?\d[/\\\-][0-3]?\d[/\\\-]\d{4})', after)
            if m_after:
                data['Ngay_sinh'] = m_after.group(1)
                date_found = True

    # Nếu vẫn chưa có, dò toàn văn bản để tìm bất kỳ ngày nào
    if not date_found:
        m_all = re.search(r'([0-3]?\d[/\\\-][0-3]?\d[/\\\-]\d{4})', normalized)
        if m_all:
            data['Ngay_sinh'] = m_all.group(1)

    # ===== Địa chỉ / Nơi cư trú / Quê quán =====
    addr_val = find_field([r'Nơi\s*cư\s*trú', r'Address', r'Địa\s*chỉ', r'Quê\s+quán'])
    if addr_val:
        # dọn dẹp tiền tố '/Address:' hoặc ký tự lạ
        addr_val = re.sub(r'^(\/?Address[:\s]*)', '', addr_val, flags=re.IGNORECASE).strip()
        data['Dia_chi'] = addr_val

    # ===== Hạng bằng (Class/Hạng) =====
    class_val = find_field([r'Hạng', r'Class', r'Loại'])
    if class_val:
        # lấy mã hạng như A1, A2, B1, B2, C, D, v.v.
        # Thử tìm các mẫu hạng bằng phổ biến (1-3 ký tự chữ hoa/số)
        mclass = re.search(r'\b([A-Z][0-9]?[12]?\b|[CDEB]\b)', class_val, re.IGNORECASE)
        if mclass:
            data['Hang'] = mclass.group(1).upper()
        # Nếu không tìm thấy, lấy 1-3 ký tự chữ hoa/số đầu tiên
        elif re.search(r'([A-Z0-9]{1,3})', class_val, re.IGNORECASE):
            data['Hang'] = re.search(r'([A-Z0-9]{1,3})', class_val, re.IGNORECASE).group(1).upper()

    # Bước 5: Kiểm tra hợp lệ
    # Lấy So_GPLX đã được chuẩn hóa (12 chữ số)
    id_num = data.get('So_GPLX', '')
    text_upper = (text_original + text_gray).upper()

    required_keywords = [
        "GPLX", "GIẤY PHÉP LÁI XE", "GIẤY PHÉPLÁIXE", "BỘ GTVT",
        "DRIVER'S LICENSE", "DRIVER LICENSE"
    ]
    is_gplx_document = has_title_found or any(keyword in text_upper for keyword in required_keywords)

    forbidden_keywords = [
        "CĂN CƯỚC CÔNG DÂN", "CCCD",
        "PASSPORT", "HỘ CHIẾU", "THẺ CĂN CƯỚC"
    ]
    is_forbidden_document = any(keyword in text_upper for keyword in forbidden_keywords)

    # Bước 6: In kết quả
    if id_num and len(id_num) == 12 and is_gplx_document and not is_forbidden_document:
        print("\n====================================")
        print("✅ Thông tin giấy phép lái xe HỢP LỆ")
        print("====================================")
        for k, v in data.items():
            print(f"{k}: {v}")
    elif not is_gplx_document:
        print("\n❌ Không tìm thấy từ khóa nhận dạng GIẤY PHÉP LÁI XE (GPLX, BỘ GTVT, v.v.).")
    elif is_forbidden_document:
        print("\n❌ Phát hiện từ khóa của tài liệu CẤM (CCCD, PASSPORT,...)")
    else:  # Trường hợp không tìm thấy đủ điều kiện (ví dụ: không đủ 12 số)
        print("\n❌ Dữ liệu không hợp lệ (Không phải GPLX, hoặc thiếu thông tin quan trọng).")

    # Bước 7: Trả về dữ liệu
    if 'So_GPLX' not in data:
        data['So_GPLX']=""
    if 'Ho_va_ten' not in data:
        data['Ho_va_ten']=""
    if 'Ngay_sinh' not in data:
        data['Ngay_sinh']=""
    if 'Dia_chi' not in data:
        data['Dia_chi']=""
    if 'Hang' not in data:
        data['Hang']=""
    data_ocr = [
        {'name':"So_GPLX",'label':"Số Giấy Phép Lái Xe",'text': data['So_GPLX']},
        {'name': "Ho_va_ten", 'label': "Họ Và Tên", 'text': data['Ho_va_ten']},
        {'name': "Ngay_sinh", 'label': "Ngày Sinh", 'text': data['Ngay_sinh']},
        {'name': "Dia_chi", 'label': "Địa Chỉ", 'text': data['Dia_chi']},
        {'name': "Hang", 'label': "Hạng", 'text': data['Hang']},
         ]
    return {
        "data": data_ocr,
        "has_title": has_title_found,
        "is_gplx_document": is_gplx_document,
        "is_valid_id_length": len(id_num) == 12
    }

def extrackIDCard():
    # Thay đổi URL nếu bạn chạy server Django trên máy khác
    OCR_API_URL = "http://localhost:80/api/idcard_extract/"

    st.title("Hệ thống Tích hợp OCR CCCD")

    uploaded_file = st.file_uploader("Tải lên ảnh CCCD (JPEG/PNG)", type=['jpg', 'png'])

    if uploaded_file is not None:
        st.image(uploaded_file, caption='Ảnh đã tải lên', width=300)

        if st.button('Xử lý OCR và Trích xuất Dữ liệu'):
            st.info("Đang gửi ảnh tới dịch vụ OCR...")

            # Chuẩn bị dữ liệu gửi đi
            # Django thường mong đợi file được gửi dưới dạng POST multipart/form-data
            files = {'selectedFile': uploaded_file.getvalue()}  # 'image' có thể là tên trường file mà Django Views mong đợi.

            try:
                # Thực hiện POST request tới API OCR
                response = requests.post(OCR_API_URL, files=files, timeout=60)  # Thiết lập timeout

                if response.status_code == 200:
                    st.success("Nhận được phản hồi 200 OK từ server OCR. Đang kiểm tra nội dung...")

                    # THÊM BƯỚC DEBUG:
                    raw_text = response.text
                    st.code(raw_text)  # Hiển thị nội dung thô nhận được từ Django

                    try:
                        # Cố gắng phân tích JSON
                        result_data = response.json()
                        st.success("✅ Phân tích JSON thành công!")
                        st.json(result_data)

                    except requests.exceptions.JSONDecodeError as e:
                        st.error(f"❌ Lỗi Phân tích JSON: {e}")
                        st.warning("Server Django đã trả về nội dung không phải JSON hợp lệ.")

                    except Exception as e:
                        st.error(f"Đã xảy ra lỗi không mong muốn: {e}")

                else:
                    # Nếu không phải 200, hiển thị lỗi server (như bạn đã làm)
                    st.error(f"❌ Lỗi API OCR: {response.status_code} - {response.text}")

            except requests.exceptions.ConnectionError:
                st.error(
                    f"⚠️ Lỗi kết nối: Không thể kết nối tới dịch vụ OCR tại {OCR_API_URL}. Vui lòng đảm bảo server Django đang chạy.")
            except Exception as e:
                st.error(f"Đã xảy ra lỗi không mong muốn: {e}")
    pass

# extrackIDCard()
API_URL = "http://localhost/api/idcard"
def upload_cccd(image_path):
    with open(image_path, "rb") as f:
        files = {"selectedFile": f}
        response = requests.post(API_URL, files=files)

    if response.status_code == 200:
        data = response.json()
        print("ID:", data.get("ID_number"))
        print("Tên:", data.get("Name"))
        print("Ngày sinh:", data.get("Date_of_birth"))
        print("Giới tính:", data.get("Gender"))
        print("Quốc tịch:", data.get("Nationality"))
        print("Quê quán:", data.get("Place_of_origin"))
        print("Nơi cư trú:", data.get("Place_of_residence"))
        return data
    else:
        print("Lỗi API:", response.text)
        return None


# Gọi thử:
# result = upload_cccd("data/db/uploads/Cancuoc_vu.jpg")

import requests
import base64

# API_URL = "http://172.20.10.2/api/idcard"
API_URL = "http://172.20.10.2/api/driverlicense"

# ================================================
# 1. Gửi ảnh dạng FILE (selectedFile)
# ================================================
def send_cccd_file(image_path):
    with open(image_path, "rb") as f:
        files = {"selectedFile": f}
        response = requests.post(API_URL, files=files)

    return process_response(response)


# ================================================
# 2. Gửi ảnh dạng BASE64 (ảnh chụp từ camera)
# ================================================
def send_cccd_base64(image_path):
    with open(image_path, "rb") as f:
        b64_data = base64.b64encode(f.read()).decode()

    payload = {"imageBase64": b64_data}
    response = requests.post(API_URL, data=payload)

    return process_response(response)


# ================================================
# Xử lý dữ liệu trả về
# ================================================
def process_response(response):
    if response.status_code != 200:
        print("Lỗi API:", response.text)
        return None

    data = response.json()
    print("===== KẾT QUẢ OCR =====")
    print("Số GPLX:", data.get("License_number"))
    print("Họ tên:", data.get("Name"))
    print("Ngày sinh:", data.get("Date_of_birth"))
    # print("Giới tính:", data.get("Gender"))
    print("Quốc tịch:", data.get("Nationality"))
    print("Hạng:", data.get("Class"))
    print("Nơi cư trú:", data.get("Address"))
    print("========================")
    return data


# ================================================
# Ví dụ sử dụng
# ================================================
if __name__ == "__main__":
    # 1. Gửi ảnh được chọn từ máy
    send_cccd_file("data/db/uploads/GPLX_mattruoc.jpg")

    # 2. Gửi ảnh chụp camera (base64)
    # send_cccd_base64("data/db/uploads/GPLX_mattruoc.jpg")