# ADR-0008: `{tenant}` nằm trong topic từ ngày đầu, Phase 0 luôn là `default`
- Status: accepted
- Date: 2026-07-15 (hồ sơ hóa từ protocol-notes mục 1.1, chốt 2026-07-09)
- Covers: [ACL-02]
## Context
Phase 0 là single-tenant (mỗi vendor một instance), nhưng Phase 1 đã chốt multi-tenant SaaS. Đổi topic layout sau khi có agent ngoài đồng nghĩa breaking change + migration mọi robot.
## Options đã cân nhắc (mục đánh * là dựng lại khi hồ sơ hóa — không có trong nguồn trích, founder xác nhận khi duyệt)
1. `mechops/v1/{tenant}/...` từ đầu, Phase 0 hardcode `default` — 2. `mechops/v1/...` không tenant, thêm khi cần — 3. Tenant trong payload thay vì topic*
## Decision
Tenant trong topic từ ngày đầu: `mechops/v1/{tenant}/agents|devices/...`. Multi-tenant Phase 1 chỉ đổi ACL (mỗi tenant một prefix), KHÔNG đổi topic layout — agent ngoài đồng không cần update. Loại tenant-trong-payload: ACL của broker match theo topic, không đọc được payload.
## Consequences
+ Migration Phase 1 = cấu hình, không phải code agent; ACL wildcard test được từ Phase 0 (ACL-02 dùng `mechops/v1/default/#`).
− Topic dài hơn một segment với người dùng single-tenant — chi phí không đáng kể.
