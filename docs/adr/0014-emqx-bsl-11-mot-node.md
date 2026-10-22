# ADR-0014: EMQX dưới BSL 1.1 — giữ cho kênh vendor một node, quyết lại trước SaaS
- Status: accepted
- Date: 2026-10-18
- Covers: [ACL-01, ACL-02, ACL-03]
- Bổ sung cho: ADR-0003 (không supersede — quyết định broker giữ nguyên, context đổi)

## Context

ADR-0003 chọn EMQX khi bản open source còn Apache 2.0. Từ EMQX 5.9 (2025) hãng hợp
nhất hai edition thành một bản duy nhất dưới **Business Source License 1.1**. Theo
FAQ license của EMQX: được sao chép, sửa, phân phối lại; **Additional Use Grant cho
phép dùng production miễn phí với một node**; cluster cần Commercial License.

Mô hình MechOps có hai kênh (03-phase-plan): kênh vendor = một instance Docker Compose
mỗi vendor (một node EMQX), và kênh SaaS multi-tenant Phase 1 do MechOps host, có thể
cần cluster.

## Options đã cân nhắc

1. **Giữ EMQX một node cho kênh vendor; quyết lại trước SaaS.** ← chọn
2. **Đổi sang Mosquitto** (EPL/EDL). Mất ACL qua PostgreSQL và MQTT 5 đầy đủ — đúng
   hai lý do ADR-0003 chọn EMQX. Phải viết plugin auth.
3. **NanoMQ** (MIT). Nhẹ, MQTT 5, nhưng auth/ACL qua HTTP hook chứ không SQL; cộng
   đồng nhỏ.
4. **Broker nhúng trong server Go** (mochi-mqtt, MIT). Bớt một container, ACL viết
   bằng Go trên cùng DB. Mất dashboard EMQX và độ chín. Hấp dẫn cho vendor nhỏ, nhưng
   là một quyết định kiến trúc lớn không nên làm cùng lúc với đổi ngôn ngữ agent.

## Decision

Phase 0 và kênh vendor: **giữ EMQX, đúng một node mỗi instance**, pin phiên bản trong
`deploy/docker-compose.yml`. `install.sh` không được sinh cluster. `docs/deploy` ghi rõ
license và điều kiện một node để vendor tự host biết họ đang dùng gì.

Trước khi mở kênh SaaS (gate Phase 1): viết ADR mới chọn giữa mua Commercial License,
hoặc broker nhúng Go (phương án 4), dựa trên số đo tải thật từ LOD-01/02 và số tenant
dự kiến. Không quyết trước khi có số.

Việc phải làm trước khi bán license đầu tiên: **xác nhận pháp lý** rằng phân phối EMQX
trong gói cài của MechOps cho vendor tự host nằm trong quyền "redistribute" của BSL 1.1
và không phải "offering EMQX as a service". Ghi kết luận vào ADR này bằng một mục nhật
ký `.steering/` trỏ về.

## Consequences

+ Không đổi gì ở Phase 0; ACL-01..03 và thiết kế ACL SQL giữ nguyên.
+ Phương án broker nhúng được giữ mở với số đo thật thay vì cảm tính.
− Có một câu hỏi pháp lý treo. Rủi ro giới hạn vì chưa bán gì trước M5.
− Nếu Phase 1 chọn mua license, chi phí vận hành SaaS tăng; nếu chọn broker nhúng, có
  hai broker phải bảo trì (EMQX cho vendor, nhúng cho SaaS). Cả hai đều là quyết định
  Phase 1, có gate tài chính đi kèm.
