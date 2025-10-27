import json

def doc_json(ten_file):
    """Đọc dữ liệu từ file JSON và trả về đối tượng Python."""
    try:
        with open(ten_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {ten_file}")
        return {} # Trả về đối tượng rỗng nếu không tìm thấy

# du_lieu = doc_json('data/user.json')
# print("Dữ liệu gốc:", du_lieu)

def ghi_json(ten_file, du_lieu):
    """Ghi đối tượng Python vào file JSON."""
    try:
        # 'w' mode (write) sẽ ghi đè lên nội dung cũ
        # indent=4 giúp file JSON dễ đọc hơn (định dạng)
        with open(ten_file, 'w', encoding='utf-8') as f:
            json.dump(du_lieu, f, indent=4, ensure_ascii=False)
        print(f"Đã lưu dữ liệu thành công vào {ten_file}")
    except Exception as e:
        print(f"Lỗi khi ghi file: {e}")

du_lieu={
    "user_id": "C001",
    "username": "nguyenvana",
    "password_hash": "hashed_password_citizen_1",
    "role": "citizen",
    "full_name": "Nguyễn Văn A",
    "email": "vana@example.com"
  }
# (Ví dụ: ghi một cấu trúc rỗng ban đầu)
ghi_json('data/db/user.json', du_lieu)

