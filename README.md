# Telegram Statistics API

Dự án này là một API được xây dựng bằng FastAPI, cho phép người dùng truy xuất và phân tích dữ liệu từ Telegram. API hỗ trợ nhiều tính năng như lấy tin nhắn, phân tích tương tác và lưu trữ dữ liệu vào MongoDB.

## Nội dung

- [Giới thiệu](#giới-thiệu)
- [Cài đặt](#cài-đặt)
- [Sử dụng](#sử-dụng)
- [API](#api)
- [Cảm ơn](#cảm-ơn)

## Giới thiệu

Telegram Statistics API cho phép bạn lấy thông tin từ các cuộc trò chuyện trên Telegram, bao gồm tin nhắn, lượt xem, và các tương tác khác. Dự án sử dụng FastAPI cho backend và MongoDB để lưu trữ dữ liệu.

## Cài đặt

1. **Clone repository:**

   ```bash
   git clone https://github.com/yourusername/telegram-statistics-api.git
   cd telegram-statistics-api
   ```

2. **Tạo và kích hoạt môi trường ảo:**

   - **Trên Windows:**

     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

   - **Trên macOS/Linux:**

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Cài đặt các phụ thuộc:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Tạo file `.env` và thêm các biến môi trường:**

   ```plaintext
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   MONGO_URI=your_mongo_uri
   BOT_TOKEN=your_bot_token
   SESSION_NAME=your_session_name
   ```

## Sử dụng

Để chạy API, bạn có thể sử dụng một trong hai cách sau:

1. **Sử dụng script `start.sh`:**

   Mở terminal và chạy lệnh sau:

   ```bash
   bash start.sh
   ```

2. **Sử dụng lệnh `uvicorn`:**

   Mở terminal và chạy lệnh sau:

   ```bash
   uvicorn app.main:app --port 8000 --reload
   ```

API sẽ chạy trên `http://localhost:8000`.

## API

### Lấy tin nhắn

- **Endpoint:** `/api/get_messages/`
- **Phương thức:** `GET`
- **Tham số:**
  - `chat_id`: ID của cuộc trò chuyện.
  - `offset_date`: Ngày bắt đầu (tùy chọn).
  - `end_date`: Ngày kết thúc (tùy chọn).
  - `keyword`: Từ khóa tìm kiếm (tùy chọn).
  - `limit`: Số lượng tin nhắn tối đa (mặc định: 100, tối đa: 1000).
  - `img_flag`: Cờ để lấy hình ảnh (mặc định: False).
  - `topic_id`: ID chủ đề (tùy chọn).
  - `fetch_username`: Cờ để lấy tên người dùng (mặc định: False).
  - `from_user`: ID người gửi (tùy chọn).

### Ví dụ

```
GET /api/get_messages/?chat_id=123456&limit=50
```

## Cảm ơn

Cảm ơn bạn đã xem dự án này! Nếu bạn có bất kỳ câu hỏi nào, hãy liên hệ với tôi qua email hoặc mở issue trên GitHub.