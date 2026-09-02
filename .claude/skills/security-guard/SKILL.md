---
name: security-guard
description: BẮT BUỘC đọc khi chạm cert/TLS, enroll token, ACL MQTT, RBAC, remote terminal/PTY, audit log, OTA digest, hoặc bất cứ chỗ nào xử lý secret. Trigger, cert, token, enroll, ACL, quyền, RBAC, terminal, PTY, digest, chữ ký, secret, mật khẩu, TLS.
paths:
  - "agent/**"
  - "server/**"
  - "deploy/**"
metadata:
  adr: [0008]
---

# Security guard

Agent chạy **quyền cao trên robot của khách hàng** và nhận lệnh từ mạng (OTA,
terminal). Một lỗ hổng ở đây không phải sự cố nội bộ — nó là truy cập vào nhà máy
của người khác. Bộ test ACL-01..04 và PRV-01..05 chính là bộ câu hỏi vendor sẽ hỏi
khi thẩm định; chúng là tính năng bán hàng, không phải phần phụ.

## Bất biến — vi phạm là chặn merge

**Danh tính & kênh**
- Mọi kết nối MQTT dùng cert client, CN = `agentId`. Không cert → chặn ở tầng TLS,
  không được lọt tới tầng auth (ACL-03).
- Enroll token dùng một lần, có hạn. Token đã dùng hoặc hết hạn → từ chối sạch,
  **không để lại rác trong DB** (PRV-02).
- Cert < 30 ngày → tự gia hạn, không gián đoạn kết nối (PRV-03). Hết hạn hoàn toàn
  → báo lỗi rõ và hướng dẫn re-enroll, **không crash-loop** (PRV-04).

**Cách ly giữa khách hàng**
- Tenant nằm trong topic từ ngày đầu (ADR-0008). Agent A không publish được vào
  topic của B (ACL-01); subscribe wildcard chỉ trả về inventory của chính nó (ACL-02).
- **Mọi query server chạm dữ liệu thiết bị phải scope theo tenant.** Query thiếu điều
  kiện tenant là rò dữ liệu khách hàng, không phải thiếu sót nhỏ.

**Bề mặt tấn công qua payload**
- Payload > 64KB: agent **từ chối trước khi publish** (ACL-04), không đẩy cho broker.
- Mọi message vào phải validate theo JSON Schema trước khi dùng. Field lạ thì bỏ qua,
  không lỗi (TEL-07) — nhưng "bỏ qua" không có nghĩa là "tin".

**OTA**
- Pull theo **digest**, không theo tag (constitution #3). Tag mutable = kênh thay thế
  artifact sau khi đã duyệt.
- Digest sai → **không start** (OTA-07). Không có chế độ "cảnh báo rồi chạy tiếp".

**Remote terminal**
- PTY là quyền admin. Role `viewer` bị từ chối (TRM-02).
- Audit log ghi **đủ input/output** của phiên (TRM-01). Terminal không có audit log
  là terminal không được phép tồn tại.
- Rớt mạng → phiên đóng sạch, không để PTY mồ côi trên robot (TRM-03).

**Secret**
- Không bao giờ log cert, private key, token, hay payload thô.
- Không commit `*.pem`, `*.key`, `.env` (đã có trong `.gitignore` — đừng thêm ngoại lệ).
- Lỗi trả cho client không được lộ nội bộ (đường dẫn file, câu SQL, phiên bản).

## Khi thêm bề mặt mới

Endpoint mới, lệnh mới, kênh mới → trả lời ba câu **trong PR**, không trong đầu:

1. Ai gọi được? (cert nào, role nào, tenant nào)
2. Gọi sai thì hỏng thế nào? (từ chối sạch hay crash)
3. Nó ghi gì vào log? (có secret không, có khoá tra cứu không)

Không trả lời được câu nào → chưa xong.

## Trước khi release

`/security-review` (skill có sẵn) trên diff, cộng với rà tay ACL EMQX và rotate cert
theo constitution #9 — release có người, không tự động.
