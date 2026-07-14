# ADR-0005: OTA rollback quyết định tại agent, không chờ server
- Status: accepted
- Date: 2026-07-15 (hồ sơ hóa từ protocol-notes mục 5, chốt 2026-07-09)
- Covers: [OTA-02, OTA-03, OTA-04, OTA-05]
## Context
Deploy hỏng trên robot có thể xảy ra đúng lúc robot mất mạng — chờ lệnh rollback từ server nghĩa là robot chết app vô hạn định.
## Options đã cân nhắc (mục đánh * là dựng lại khi hồ sơ hóa — không có trong nguồn trích, founder xác nhận khi duyệt)
1. Rollback tự trị tại agent (health check local) — 2. Server quyết định rollback qua lệnh — 3. Blue-green với 2 bản chạy song song* (loại: robot không đủ tài nguyên chạy đôi)
## Decision
Ba luật cứng trong state machine OTA của agent (persist SQLite local):
1. Health check fail hoặc container crash-loop → tự `ROLLING_BACK` không cần lệnh server.
2. Mọi chuyển state ghi SQLite TRƯỚC hành động — boot lên thấy state dở dang (`DOWNLOADING`/`SWITCHING`) coi như fail, rollback về version cũ còn nguyên trên đĩa (OTA-04/05: rút điện giữa chừng).
3. Pull theo digest, không theo tag — tag bị ghi đè trên registry không được đổi thứ robot chạy (OTA-07).
Staged rollout là logic server (chọn wave, chờ SUCCESS) — protocol không đổi, agent không biết wave.
## Consequences
+ Robot không bao giờ ở trạng thái "không có app nào chạy"; sống sót mất điện/mất mạng giữa deploy.
− Agent phức tạp hơn (state machine + SQLite + health check executor); image cũ chiếm đĩa thêm `keepPreviousHours`.
