# RobotOps — Phase 0 Acceptance Test Catalog

> Vai trò: **định nghĩa "xong" cuối cùng** của Phase 0. Mỗi milestone chỉ đóng khi các test của nó pass. Mỗi test có ID cố định — dùng trong CI, trong PR description, và làm context cho Claude Code.
> Ba tầng test:
> - **[U]** Unit/contract — chạy trong CI mỗi PR (validate bằng JSON Schema + test vector của protocol spec mục 9)
> - **[I]** Integration — docker-compose + agent giả lập, chạy trong CI nightly
> - **[H]** Hardware-in-the-loop — Jetson + Pi thật, chạy tay trước mỗi release, có checklist ký tên

---

## A. Provisioning & danh tính (M1)

| ID | Tầng | Kịch bản | Kết quả mong đợi |
|---|---|---|---|
| PRV-01 | I | Enroll với token hợp lệ | Agent nhận cert CN=agentId, connect MQTT thành công, xuất hiện trên dashboard < 10s |
| PRV-02 | I | Enroll với token đã dùng / hết hạn | Bị từ chối, lỗi rõ ràng trên CLI, không tạo rác trong DB |
| PRV-03 | I | Cert còn < 30 ngày | Agent tự gia hạn, không gián đoạn kết nối MQTT |
| PRV-04 | I | Cert hết hạn hoàn toàn (robot tắt 4 tháng) | Agent báo lỗi rõ, hướng dẫn re-enroll; không crash-loop |
| PRV-05 | H | Enroll trên Jetson + Pi từ script `curl \| sh` | Cài + enroll xong < 5 phút mỗi máy, theo đúng docs |

## B. ACL & cách ly (M1) — *bộ test bán hàng: vendor sẽ hỏi đúng những câu này*

| ID | Tầng | Kịch bản | Kết quả mong đợi |
|---|---|---|---|
| ACL-01 | I | Agent A publish vào topic của agent B | Broker từ chối (disconnect hoặc drop theo cấu hình EMQX), có log |
| ACL-02 | I | Agent A subscribe wildcard `robotops/v1/default/#` | Chỉ nhận được topic thuộc inventory của chính nó |
| ACL-03 | I | Client không có cert connect broker | Từ chối ở tầng TLS, không tới được tầng auth |
| ACL-04 | I | Agent gửi payload > 64KB | Agent từ chối trước khi publish (theo protocol spec 9); server cũng drop nếu nhận được |

## C. Telemetry, state, events (M1–M2)

| ID | Tầng | Kịch bản | Kết quả mong đợi |
|---|---|---|---|
| TEL-01 | U | Mọi payload mẫu trong `/schemas/testvectors` | Validate pass/fail đúng như đánh dấu |
| TEL-02 | I | Agent chạy 24h liên tục | Không memory leak (RSS ổn định), `seq` không tụt, không trùng |
| TEL-03 | I | Rút mạng agent 5 phút | LWT phát trong ≤ keepalive×1.5; dashboard hiện offline; mọi device trong inventory chuyển offline |
| TEL-04 | I | Reconnect sau TEL-03 | State retained cập nhật online; events buffer replay đủ, đúng thứ tự `seq`, `ts` gốc giữ nguyên |
| TEL-05 | I | Mất mạng 24h+ | Telemetry buffer downsample 30s, không vượt trần 24h; reconnect không làm nghẽn broker (đo băng thông replay) |
| TEL-06 | I | Lệch giờ hệ thống > 30s so NTP | Event `agent.clock_skew` phát ra, hiển thị cảnh báo trên device detail |
| TEL-07 | H | Field lạ trong payload (giả lập version mới) | Agent/server bỏ qua field lạ, không lỗi (forward-compat theo spec mục 1) |

## D. Probe API (M2)

| ID | Tầng | Kịch bản | Kết quả mong đợi |
|---|---|---|---|
| PRB-01 | U | Handshake với `apiVersion` không hỗ trợ | `accepted:false` + lý do; agent không crash |
| PRB-02 | I | ros2-probe khai 1 device, gửi data AMR profile | Battery + pose hiện trên dashboard, đúng envelope `profiles.amr` |
| PRB-03 | I | Kill probe process | 3 ping không pong → device chuyển `degraded` + event; agent vẫn sống, OTA vẫn hoạt động |
| PRB-04 | I | Probe restart, handshake lại | Device về trạng thái bình thường, inventory không nhân đôi |
| PRB-05 | I | 2 probe đồng thời trên 1 agent (giả lập Mode B) | Inventory hợp nhất đúng N device; data không lẫn deviceId |
| PRB-06 | H | Node ROS 2 chết trên robot thật (kill nav2) | Event `ROS_NODE_DOWN` ≤ 10s, alarm hiện trên dashboard |

## E. OTA (M3) ⭐ — *bộ test quan trọng nhất Phase 0, mọi ID phải pass trên phần cứng thật*

| ID | Tầng | Kịch bản | Kết quả mong đợi |
|---|---|---|---|
| OTA-01 | I/H | Deploy version mới, health check pass | State machine đi đủ DOWNLOADING→…→SUCCESS; app mới chạy; image cũ dọn sau `keepPreviousHours` |
| OTA-02 | I/H | Deploy version có health check fail | Tự ROLLING_BACK→ROLLED_BACK **không cần lệnh server**; app cũ chạy lại; dashboard hiện đúng lý do |
| OTA-03 | I/H | Container mới crash-loop (chết trước cả health check) | Như OTA-02 — rollback cục bộ |
| OTA-04 | H | **Rút điện giữa DOWNLOADING** | Boot lên: agent thấy state dở dang → coi như fail → app cũ chạy bình thường, không mất dữ liệu |
| OTA-05 | H | **Rút điện giữa SWITCHING** | Boot lên: rollback về version cũ còn nguyên trên đĩa; robot không bao giờ ở trạng thái "không có app nào chạy" |
| OTA-06 | I | Rút mạng giữa DOWNLOADING | Retry có backoff; mạng về thì tiếp tục hoặc fail sạch sẽ — không treo vô hạn |
| OTA-07 | I | Digest không khớp image (giả mạo/hỏng) | VERIFYING fail → FAILED, không bao giờ start container sai digest |
| OTA-08 | I | Lệnh deploy có `expiresAt` quá hạn (agent offline 3 ngày mới nhận) | `rejected/expired`, không thực thi |
| OTA-09 | I | Staged rollout 3 nhóm, nhóm 1 fail | Fleet Manager dừng, không đẩy nhóm 2–3; trạng thái wave rõ trên dashboard |
| OTA-10 | I | Gửi deploy mới khi deploy cũ đang chạy | Từ chối có lý do (một deployment tại một thời điểm) — không race |
| OTA-11 | H | Disk gần đầy (< dung lượng image mới) | Fail sạch ở DOWNLOADING với lỗi rõ ràng, không làm hỏng app đang chạy |
| OTA-12 | H | Toàn bộ OTA-01→05 trên cả Jetson **và** Pi | Ma trận bắt buộc trước mỗi release agent |

## F. Alert & notification (M4)

| ID | Tầng | Kịch bản | Kết quả mong đợi |
|---|---|---|---|
| ALT-01 | I | Robot offline > ngưỡng cấu hình | Email + Telegram/Zalo trong ≤ 60s |
| ALT-02 | I | Battery dưới ngưỡng rồi hồi lại | Alarm raised → cleared; notification không spam lặp (cooldown) |
| ALT-03 | I | 50 robot giả lập cùng offline (mất điện xưởng) | Notification gộp/ngưỡng chống bão, không bắn 50 tin riêng |
| ALT-04 | I | Webhook endpoint chết | Retry có giới hạn, lỗi hiển thị trong dashboard, không chặn alert khác |

## G. Remote terminal & log (M4–M5)

| ID | Tầng | Kịch bản | Kết quả mong đợi |
|---|---|---|---|
| TRM-01 | I | Mở phiên terminal, chạy lệnh, đóng | PTY hoạt động; **audit log đầy đủ input/output**, xem lại được từ dashboard |
| TRM-02 | I | User role `viewer` mở terminal | Bị từ chối — terminal là quyền admin |
| TRM-03 | I | Rớt mạng giữa phiên | Phiên đóng sạch ≤ 30s, không để PTY mồ côi trên robot |
| TRM-04 | I | Log tail bật rồi quên | Tự tắt sau TTL (mặc định 15 phút) — không stream vô hạn tốn băng thông |

## H. White-label & installer (M5) — *test bằng người thật*

| ID | Tầng | Kịch bản | Kết quả mong đợi |
|---|---|---|---|
| WLB-01 | I | Đổi logo + màu qua config instance | Dashboard phản ánh, không cần rebuild image |
| INS-01 | H | Người ngoài team cài instance mới theo docs, VPS trống | Xong < 30 phút, không cần hỏi ai (đúng DoD của M5) |
| INS-02 | I | `install.sh` chạy lại trên máy đã cài (idempotent) | Không phá dữ liệu, báo trạng thái đúng |
| INS-03 | I | Backup/restore Postgres volume theo docs | Instance mới nhận dữ liệu cũ đầy đủ, device reconnect bình thường |

## I. Tải & bền bỉ (M6 — hardening)

| ID | Tầng | Kịch bản | Kết quả mong đợi |
|---|---|---|---|
| LOD-01 | I | 50 agent giả lập, telemetry 2s/lần, 72h | Không mất event QoS 1; TimescaleDB compression chạy; dashboard vẫn phản hồi < 2s |
| LOD-02 | I | 50 agent reconnect đồng loạt sau khi broker restart | Bão replay không đánh sập server; backpressure hoạt động |
| LOD-03 | H | Fleet design partner chạy 30 ngày | Không sự cố brick (bằng chứng cho North Star tháng 9); uptime agent ≥ 99.5% |

---

## Quy tắc vận hành catalog

1. **Mỗi PR khai báo ID test nó ảnh hưởng** — Claude Code đưa được quy tắc này vào workflow qua CLAUDE.md của repo.
2. **[H] có checklist giấy/markdown ký tên + ngày** trong `/docs/hw-test-runs/` — kỷ luật này rẻ, còn robot brick tại khách thì không.
3. Bug mới phát hiện → **thêm test ID mới trước khi sửa** — catalog chỉ phình ra, không teo lại.
4. Release agent = OTA-12 pass + toàn bộ [U][I] xanh trong CI. Không ngoại lệ, kể cả "chỉ sửa một dòng".
