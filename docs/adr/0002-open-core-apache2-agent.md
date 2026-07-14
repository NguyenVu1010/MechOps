# ADR-0002: Open-core — agent Apache 2.0, server closed
- Status: accepted
- Date: 2026-07-15 (hồ sơ hóa từ spec v2 mục 7, chốt 2026-07-09)
## Context
Agent chạy trên robot của khách hàng — vendor sẽ muốn audit code chạy trong hạ tầng của họ. Đồng thời cần kênh marketing chi phí 0 trong cộng đồng ROS 2, và cần phần thu tiền được bảo vệ.
## Options đã cân nhắc (mục đánh * là dựng lại khi hồ sơ hóa — không có trong nguồn trích, founder xác nhận khi duyệt)
1. Open-core (agent + protocol open, server closed) — 2. Toàn bộ closed* — 3. Toàn bộ open + thu tiền hosting/support*
## Decision
Open-core theo bảng spec v2 mục 7: `mechops-agent` Apache 2.0 public GitHub; protocol spec open (license Apache 2.0 đã khai trong `specs/asyncapi.yaml`); ranh giới open gồm `agent/`, `probe/`, `protocol/`, `specs/` (như README ghi từ đầu). Server, dashboard, OTA orchestration, Fleet Manager closed trả phí. Playbook tham chiếu: Mender, balena, Grafana.
## Consequences
+ Vendor audit được thứ chạy trên robot của họ → lòng tin; cộng đồng viết adapter trên protocol open; lan truyền ROS 2 miễn phí.
− Ranh giới open/closed phải giữ kỷ luật từng PR — code server không được rò vào repo public; agent không được import gì từ phần closed.
