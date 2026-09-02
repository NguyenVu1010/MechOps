# .steering — dòng thời gian

> ⚙️ Sinh bởi `tools/steering/steer.py` — **không sửa tay**. Trạng thái hiện tại: `INDEX.md`.
> 42 sự việc · plan · cổng chốt · mục nhật ký · ADR, mới nhất trên đầu

| Mốc (UTC) | Loại | Việc |
|---|---|---|
| `2026-09-02T07:05:22Z` | risky | đóng [S0015](entries/2026-09-02T070512Z-S0015-risky-set-e-echo-steering-dang-treo-gi-bash-mo-s.md) **kept** → none — day la he qua cua ruleset, khong phai bai hoc moi |
| `2026-09-02T07:05:12Z` | risky | mở [S0015](entries/2026-09-02T070512Z-S0015-risky-set-e-echo-steering-dang-treo-gi-bash-mo-s.md) — set +e ; echo === .steering đang treo gì === ; bash ./mo steer pla |
| `2026-09-01T06:23:20Z` | decision | đóng [S0014](entries/2026-09-01T062319Z-S0014-decision-dev-moi-vibe-khong-chan-phien-chan-ba-lo-c.md) **kept** → Makefile check-merge + trace.py check_no_skip + trace.py check_deleted_plans + session-start.sh tu bat hook |
| `2026-09-01T06:23:19Z` | decision | mở [S0014](entries/2026-09-01T062319Z-S0014-decision-dev-moi-vibe-khong-chan-phien-chan-ba-lo-c.md) — Dev moi vibe: khong chan phien, chan ba lo cu the · **quyết định:** Khong dat rao can nao truoc phien vibe. Thay vao do: session-start tu bat git hook, va ba luat chi-nam-trong-van-ban (conflict marker, t.Skip, xoa plan) tro thanh chot chan may. |
| `2026-09-01T03:56:53Z` | risky | đóng [S0013](entries/2026-09-01T035545Z-S0013-risky-git-checkout----docstest-statusjson-docste.md) **reverted** → none — hook bao dung, day la rm -rf that |
| `2026-09-01T03:55:45Z` | risky | mở [S0013](entries/2026-09-01T035545Z-S0013-risky-git-checkout----docstest-statusjson-docste.md) — git checkout -- docs/test-status.json docs/test-status.md && rm -rf d |
| `2026-08-25T19:51:53Z` | risky | đóng [S0012](entries/2026-08-25T194921Z-S0012-risky-cd-cusersanhnd0904workspacemechops-docker.md) **kept** → trace.py check_exec_bits() — MUST_EXEC phai la 100755 |
| `2026-08-25T19:49:21Z` | risky | mở [S0012](entries/2026-08-25T194921Z-S0012-risky-cd-cusersanhnd0904workspacemechops-docker.md) — cd /c/Users/AnhND0904/workspace/MechOps ; docker compose -f docker-com |
| `2026-08-25T19:35:07Z` | risky | đóng [S0011](entries/2026-08-25T193404Z-S0011-risky-cd-cusersanhnd0904workspacemechops-bash-mo.md) **reverted** → record-risky.sh: bo gia tri --why/--title/--promoted/-m... ; ma tran 24 ca |
| `2026-08-25T19:34:06Z` | risky | đóng [S0010](entries/2026-08-25T193137Z-S0010-risky-cd-cusersanhnd0904workspacemechops-git-add.md) **reverted** → record-risky.sh: scan=${cmd%%<<*} + _lib.sh json_str xu ly dau escape; ma tran 20 ca trong scratchpad |
| `2026-08-25T19:34:04Z` | risky | mở [S0011](entries/2026-08-25T193404Z-S0011-risky-cd-cusersanhnd0904workspacemechops-bash-mo.md) — cd /c/Users/AnhND0904/workspace/MechOps ; bash ./mo steer close S0010 |
| `2026-08-25T19:31:37Z` | risky | mở [S0010](entries/2026-08-25T193137Z-S0010-risky-cd-cusersanhnd0904workspacemechops-git-add.md) — cd /c/Users/AnhND0904/workspace/MechOps ; git add -A ; git commit -F - |
| `2026-08-25T19:13:40Z` | decision | đóng [S0009](entries/2026-08-25T191339Z-S0009-decision-contract-noi-plan-vao-specs-bang-thu-may-k.md) **kept** → tools/checks/contract_touch.py + buoc CI 'specs/ doi phai co plan khai truoc' |
| `2026-08-25T19:13:39Z` | decision | mở [S0009](entries/2026-08-25T191339Z-S0009-decision-contract-noi-plan-vao-specs-bang-thu-may-k.md) — contract: noi plan vao specs bang thu may kiem duoc · **quyết định:** spec.md khai contract: [file/thu muc trong specs/]; CI doi chieu diff specs/ voi danh sach do |
| `2026-08-25T18:48:19Z` | decision | đóng [S0008](entries/2026-08-25T184817Z-S0008-decision-bo-sung-format-quyet-dinh-dong-bo-nhieu-nh.md) **kept** → trace.py: enum + decision bat buoc; next.py: pha CAN NGUOI QUYET; pr.yml: chot chan .steering khong lech |
| `2026-08-25T18:48:17Z` | decision | mở [S0008](entries/2026-08-25T184817Z-S0008-decision-bo-sung-format-quyet-dinh-dong-bo-nhieu-nh.md) — Bo sung format quyet dinh, dong bo nhieu nhanh, va triage plan treo · **quyết định:** moi ban tin mang decision/reversible/deciders/revisit + muc Da can nhac; plan treo do ./mo steer plan triage hoi va chi tra loi bang keep/abandon · đảo lại: costly |
| `2026-08-25T18:29:04Z` | wrong | đóng [S0007](entries/2026-08-25T182903Z-S0007-wrong-xoa-plan-m1-provisioning-mot-phien-plan-bi.md) **kept** → ./mo steer plan abandon + trace: supersedes phai tro plan co that + CLAUDE.md cam xoa thu muc plan |
| `2026-08-25T18:29:03Z` | wrong | mở [S0007](entries/2026-08-25T182903Z-S0007-wrong-xoa-plan-m1-provisioning-mot-phien-plan-bi.md) — Xoa plan m1-provisioning — mot phien plan bien mat khong dau vet |
| `2026-08-25T18:28:38Z` | risky | đóng [S0006](entries/2026-08-25T182805Z-S0006-risky-cd-cusersanhnd0904workspacemechops-docker.md) **kept** → none |
| `2026-08-25T18:28:37Z` | risky | đóng [S0005](entries/2026-08-25T182714Z-S0005-risky-cd-cusersanhnd0904workspacemechops-docker.md) **kept** → none — test trong ban sao, khong co gi de nang len |
| `2026-08-25T18:28:05Z` | risky | mở [S0006](entries/2026-08-25T182805Z-S0006-risky-cd-cusersanhnd0904workspacemechops-docker.md) — cd /c/Users/AnhND0904/workspace/MechOps ; docker compose -f docker-com |
| `2026-08-25T18:27:14Z` | risky | mở [S0005](entries/2026-08-25T182714Z-S0005-risky-cd-cusersanhnd0904workspacemechops-docker.md) — cd /c/Users/AnhND0904/workspace/MechOps ; docker compose -f docker-com |
| `2026-08-25T18:12:58Z` | decision | đóng [S0004](entries/2026-08-25T181248Z-S0004-decision-ten-file-steering-gan-moc-thoi-gian-utc-o.md) **kept** → trace.py: moc trong ten file phai khop date: — CI do neu doi ten tay |
| `2026-08-25T18:12:48Z` | decision | mở [S0004](entries/2026-08-25T181248Z-S0004-decision-ten-file-steering-gan-moc-thoi-gian-utc-o.md) — Ten file steering gan moc thoi gian UTC o dau · **quyết định:** Ten file steering gan moc thoi gian UTC o dau |
| `2026-08-24T18:30:03Z` | plan | mở plan **[m1-contract-v01](plans/m1-contract-v01/)** · M1 · covers [TEL-01, TEL-07] |
| `2026-08-23T08:59:48Z` | risky | đóng [S0003](entries/2026-08-23T085925Z-S0003-risky-cd-cusersanhnd0904workspacemechopsnrm--rf.md) **reverted** → none — tracker da co hook chan ghi tay, day chi la don du lieu gia lap |
| `2026-08-23T08:59:25Z` | risky | mở [S0003](entries/2026-08-23T085925Z-S0003-risky-cd-cusersanhnd0904workspacemechopsnrm--rf.md) — cd /c/Users/AnhND0904/workspace/MechOps/nrm -rf docs/evidence/ci/2026- |
| `2026-08-23T06:37:18Z` | discovery | đóng [S0002](entries/2026-08-23T063717Z-S0002-discovery-4-skill-co-frontmatter-yaml-khong-hop-le-m.md) **kept** → trace.py check_frontmatter() — CI bat thay vi dua vao may man |
| `2026-08-23T06:37:17Z` | discovery | mở [S0002](entries/2026-08-23T063717Z-S0002-discovery-4-skill-co-frontmatter-yaml-khong-hop-le-m.md) — 4 skill co frontmatter YAML khong hop le ma van chay |
| `2026-08-23T06:37:16Z` | wrong | đóng [S0001](entries/2026-08-23T063715Z-S0001-wrong-golangci-lint-chay-duoc-voi-trong-gowork.md) **reverted** → none — da co chu thich canh GO_PKGS trong Makefile:8 |
| `2026-08-23T06:37:15Z` | wrong | mở [S0001](entries/2026-08-23T063715Z-S0001-wrong-golangci-lint-chay-duoc-voi-trong-gowork.md) — golangci-lint chay duoc voi ./... trong go.work |
| `2026-08-23T00:00:00Z` | ADR | [ADR-0010: Toolchain dev nằm trong Docker, `./mo` là entrypoint duy nhất](../docs/adr/0010-toolchain-trong-docker.md) · accepted |
| `2026-08-23T00:00:00Z` | ADR | [ADR-0011: Mỗi luật của repo phải có một chốt chặn máy kiểm, không chỉ một dòng văn bản](../docs/adr/0011-cuong-che-trong-ci-khong-trong-van-ban.md) · accepted |
| `2026-07-15T00:00:00Z` | ADR | [ADR-0002: Open-core — agent Apache 2.0, server closed](../docs/adr/0002-open-core-apache2-agent.md) · accepted |
| `2026-07-15T00:00:00Z` | ADR | [ADR-0003: EMQX làm broker, không dùng Mosquitto](../docs/adr/0003-emqx-over-mosquitto.md) · accepted |
| `2026-07-15T00:00:00Z` | ADR | [ADR-0004: Probe tách khỏi agent, nói chuyện qua Unix socket](../docs/adr/0004-probe-api-unix-socket.md) · accepted |
| `2026-07-15T00:00:00Z` | ADR | [ADR-0005: OTA rollback quyết định tại agent, không chờ server](../docs/adr/0005-ota-rollback-at-agent.md) · accepted |
| `2026-07-15T00:00:00Z` | ADR | [ADR-0006: PostgreSQL 16 + TimescaleDB, một database duy nhất](../docs/adr/0006-timescaledb-over-influx.md) · accepted |
| `2026-07-15T00:00:00Z` | ADR | [ADR-0007: Dashboard realtime qua SSE từ API server, không MQTT-over-WebSocket](../docs/adr/0007-sse-not-mqtt-websocket.md) · accepted |
| `2026-07-15T00:00:00Z` | ADR | [ADR-0008: `{tenant}` nằm trong topic từ ngày đầu, Phase 0 luôn là `default`](../docs/adr/0008-tenant-in-topic-from-day-one.md) · accepted |
| `2026-07-15T00:00:00Z` | ADR | [ADR-0009: Go cho agent + server, không dùng C++](../docs/adr/0009-go-not-cpp-for-agent.md) · accepted |
| `2026-07-09T00:00:00Z` | ADR | [ADR-0001: MQTT làm transport, không tự xây trên TCP](../docs/adr/0001-mqtt-over-custom-tcp.md) · accepted |
