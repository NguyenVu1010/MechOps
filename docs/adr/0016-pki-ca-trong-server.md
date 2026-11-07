# ADR-0016: PKI thiết bị — CA nằm trong server, cert 90 ngày, enroll token một lần
- Status: accepted
- Date: 2026-10-18
- Covers: [PRV-01, PRV-02, PRV-03, PRV-04, ACL-03]

## Context

Toàn bộ nhóm PRV và ACL-03 phụ thuộc vào câu hỏi chưa có ADR: ai ký cert cho agent,
cert sống bao lâu, gia hạn qua đâu, thu hồi thế nào. `docs/protocol-notes.md` mục 2 mô
tả luồng (token → CSR → cert CN=agentId, 90 ngày, gia hạn khi còn < 30 ngày) nhưng
không nói CA là gì. Đây là việc đầu tiên của M1 nên phải quyết trước `/task PRV-01`.

Ràng buộc: team part-time (mỗi service thêm là chi phí vĩnh viễn, ADR-0006), instance
chạy on-premise tại vendor có thể không có Internet ra ngoài, EMQX xác thực client
bằng cert và lấy username từ CN để tra ACL SQL (ADR-0003).

## Options đã cân nhắc

1. **CA tối giản trong server Go, dùng `crypto/x509` stdlib.** ← chọn. ~300 dòng,
   không thêm service, không thêm dependency.
2. **smallstep step-ca.** Đầy đủ (ACME, OIDC, SSH CA), nhưng là một service nữa với
   DB riêng, và 95% tính năng không dùng.
3. **HashiCorp Vault PKI.** Quá nặng cho một instance vendor; license BSL.
4. **Cert tự ký per-agent, server lưu fingerprint (pinning).** Không cần CA, nhưng
   EMQX không xác thực được ở tầng TLS → mất ACL-03.

## Decision

**Mỗi instance có một CA riêng**, sinh lúc `install.sh` chạy lần đầu, do server Go ký
bằng `crypto/x509`:

| Thành phần | Quyết định |
|---|---|
| Root CA | Một cấp, RSA 4096 hoặc ECDSA P-384, TTL 10 năm. Khoá lưu trong volume `ca/`, mã hoá bằng `MECHOPS_CA_PASSPHRASE` từ env. Không có intermediate ở Phase 0. |
| Enroll token | 32 byte random, lưu **hash** trong bảng `enroll_tokens`, TTL 24h, dùng một lần, gắn `createdBy`. Hết hạn hoặc đã dùng → 403 với lý do, không tạo gì trong DB (PRV-02). |
| Enroll | `POST /v1/enroll` qua HTTPS (server cert do CA này ký, hoặc cert public của vendor). Body: token + CSR (PEM). Server kiểm token, sinh `agentId`, ký cert **CN=agentId**, TTL 90 ngày, trả cert + CA chain + cấu hình MQTT. Transaction: token đánh dấu dùng và agent tạo trong cùng một transaction. |
| Khoá agent | Sinh tại agent (rcgen, ECDSA P-256), không bao giờ rời thiết bị. Lưu `/var/lib/mechops/identity/` quyền 0600. |
| Gia hạn | `POST /v1/agents/me/renew` qua **mTLS bằng cert hiện tại**, khi còn < 30 ngày. Server ký cert mới cùng CN. Agent reconnect MQTT bằng cert mới không ngắt phiên cũ trước khi phiên mới lên (PRV-03). |
| Hết hạn hoàn toàn | Agent kiểm `NotAfter` lúc khởi động. Hết hạn → log lỗi rõ, in hướng dẫn `mechops-agent enroll`, thoát mã 78 (EX_CONFIG), systemd `Restart=on-failure` với `RestartSec=300` để không crash-loop (PRV-04). |
| EMQX | `ssl.verify = verify_peer`, `fail_if_no_peer_cert = true` (ACL-03), `peer_cert_as_username = cn`. ACL SQL tra theo username = agentId. |
| Thu hồi | Phase 0 không CRL/OCSP. Thu hồi = xoá dòng ACL + đặt `agents.revoked_at`; cert 90 ngày là giới hạn thiệt hại. Ghi rõ trong docs bảo mật. CRL xét ở Phase 1 cùng Keycloak. |

Bảng SQL: `enroll_tokens(id, token_hash, expires_at, used_at, created_by)`,
`agents(agent_id, cert_serial, cert_not_after, revoked_at, enrolled_at)`.
Query qua sqlc như mọi query khác.

## Consequences

+ Không thêm service. Toàn bộ PKI là một package `server/internal/ca` và hai bảng.
+ On-premise không cần Internet: CA sống trong instance.
+ ACL-03 kiểm ở tầng TLS của broker, không tới tầng auth.
− Mất khoá CA = phải enroll lại toàn fleet. Giảm bằng INS-03 (backup/restore volume
  gồm `ca/`) và passphrase tách khỏi volume.
− Không có thu hồi tức thời. Chấp nhận với cert 90 ngày và ACL deny; Phase 1 xét CRL.
− Server cert cho HTTPS/SSE do CA này ký thì browser cảnh báo; vendor cài cert public
  riêng (Let's Encrypt hoặc của họ) cho dashboard. Hai CA, hai mục đích, ghi trong docs deploy.
