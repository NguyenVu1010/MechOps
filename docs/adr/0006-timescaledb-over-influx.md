# ADR-0006: PostgreSQL 16 + TimescaleDB, một database duy nhất
- Status: accepted
- Date: 2026-07-15 (hồ sơ hóa từ dev-plan mục 1.3, chốt 2026-07-09)
## Context
Cần lưu cả relational (users, devices, deployments) lẫn time-series (telemetry). Team part-time — mỗi service thêm vào là chi phí vận hành vĩnh viễn.
## Options đã cân nhắc (mục đánh * là dựng lại khi hồ sơ hóa — không có trong nguồn trích, founder xác nhận khi duyệt)
1. PostgreSQL + TimescaleDB extension — 2. PostgreSQL + InfluxDB riêng cho time-series — 3. PostgreSQL thuần (partition tay)*
## Decision
Một PostgreSQL 16 + TimescaleDB: telemetry vào hypertable với compression + retention (raw 7 ngày, downsample 1-phút giữ 90 ngày). Loại InfluxDB: thêm một query language + một service phải vận hành, không đáng khi TimescaleDB đủ tốt tới hàng trăm nghìn point/giây. Redis cũng CHƯA dùng — `LISTEN/NOTIFY` + cache in-memory đủ cho single-tenant; thêm khi có số đo chứng minh.
## Consequences
+ Một database để backup/migrate/vận hành; SQL thuần qua sqlc cho cả hai loại dữ liệu.
− Trần scale thấp hơn Influx chuyên dụng — chấp nhận, single-tenant Phase 0 còn xa trần; xét lại khi multi-tenant Phase 1 có số đo.
