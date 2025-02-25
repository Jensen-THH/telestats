http://localhost:8000/api/get_messages/?
chat_id=nghienplusofficial
&username_filter=kaidevv
&topic_id=88317
&start_date=2025-01-01T00:00:00
&end_date=2025-02-28T23:59:59
&limit=100
&keyword=blockchain
&img_flag=true

========================
| Tham số         | Giá trị ví dụ            | Giải thích |
|-----------------|------------------------- |------------|
| chat_id         | nghienplusofficial       | ID hoặc username của group/channel cần lấy tin nhắn |
| username_filter | kaidevv                  | Lọc tin nhắn theo username của người gửi |
| topic_id        | 88317                    | Lọc tin nhắn thuộc một topic cụ thể trong group |
| start_date      | 2025-01-01T00:00:00      | Lọc tin nhắn từ ngày 01/01/2025 |
| end_date        | 2025-02-28T23:59:59      | Lọc tin nhắn đến ngày 28/02/2025 |
| keyword         | blockchain               | Chỉ lấy tin nhắn có chứa từ khóa "blockchain" |
| limit           | 100                      | Số lượng tin nhắn tối đa cần lấy (giới hạn để tránh quá tải) |
| img_flag        | true                     | `true` để tải hình ảnh/tệp đính kèm dưới dạng base64, `false` nếu không cần |
                                                kèm dưới dạng base64, false nếu không cần
checkport debug
netstat -ano | findstr :8000      
taskkill /PID 3740  /F