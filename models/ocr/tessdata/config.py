import pytesseract
import os

# Đường dẫn cài đặt Tesseract trên Windows
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Thiết lập đường dẫn cho pytesseract
# Đây là bước BẮT BUỘC trên Windows để pytesseract hoạt động
pytesseract.tesseract_cmd = TESSERACT_PATH

# Đường dẫn tới thư mục tessdata (chứa gói ngôn ngữ)
# Thường không cần thiết lập riêng vì Tesseract tự tìm,
# nhưng hữu ích để kiểm tra hoặc trong môi trường phức tạp.
TESSDATA_DIR = r"C:\Program Files\Tesseract-OCR\tessdata"
os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR