# RobotOps Constitution — nguyên tắc bất khả thương lượng

1. **TDD bắt buộc.** Không viết implementation trước khi test tồn tại và ĐỎ. Test đỏ = việc chưa xong, không phải thứ để skip.
2. **Tick chỉ do máy.** test-status.* do track.py ghi. Mọi ✅ có evidence trỏ được (raw log + commit, hoặc biên bản [H] có ký tên).
3. **OTA ba luật cứng:** rollback quyết định tại agent · mọi chuyển state ghi SQLite TRƯỚC hành động · pull theo digest, không theo tag.
4. **Spec thắng code.** Contract nằm ở specs/ (AsyncAPI + JSON Schema). Code lệch spec là bug của code. Đổi nghĩa field = breaking change = quyết định của founder, agent dừng và hỏi.
5. **Một công nghệ mỗi lớp.** Go · MQTT/EMQX · PostgreSQL+TimescaleDB · Next.js · Docker Compose. Thêm dependency mới phải qua ADR.
6. **Mọi "tự xây" phải trả lời "vì sao không dùng OSS có sẵn"** — bằng ADR.
7. **Agent không import code server.** Chiều phụ thuộc: server → protocol ← agent. Không bao giờ ngược.
8. **Quyết định ghi bằng ADR, bất biến.** Đổi ý → ADR mới supersede, không sửa cũ.
9. **Không tự động hóa:** merge main, sửa specs/, tick [H], release — luôn có người.
