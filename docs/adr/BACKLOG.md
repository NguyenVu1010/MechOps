# ADR backlog

Đã hồ sơ hóa 0002..0009 (open-core, EMQX, probe unix socket, OTA rollback tại agent, TimescaleDB, SSE, tenant trong topic, Go vs C++) — 2026-07-15.

Đã hồ sơ hóa 0010..0011 (toolchain dev trong Docker + `./mo`; cưỡng chế luật bằng máy thay vì văn bản) — 2026-08-23.

Chờ viết khi build:
- WebRTC/Pion cho video (Phase 1, xem ADR-0001 Consequences)
- Foxglove thay tự xây visualization (Phase 1)
- JWT tự triển khai vs Keycloak (khi multi-tenant)
- **Review PR bằng `anthropics/claude-code-action`** — hiện dùng `REVIEW.md` +
  `/code-review` local (ADR-0011 Decision). Xét lại khi có người thứ ba vào dự án,
  vì lúc đó review không còn đi qua một cái máy duy nhất.
- **Headless `claude -p` chạy task từ issue có label `agent-ok`** — nấc tự động hoá
  thứ 2 trong `06-spec-management.md`, dự kiến cuối M2 khi đã đủ tin cậy.
