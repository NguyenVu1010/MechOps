# .steering — mục lục

> ⚙️ Sinh bởi `tools/steering/steer.py` — **không sửa tay**. Luật và format: `.steering/README.md`.
> 1 plan · 11 mục nhật ký · 0 chưa đóng · decision 3 · discovery 1 · risky 5 · wrong 2

## Plan đang mở

| Plan | Milestone | Trạng thái | Covers | ADR | Bị thay bởi | Nhật ký |
|---|---|---|---|---|---|---|
| [m1-contract-v01](plans/m1-contract-v01/) | M1 | 0/4 chốt | TEL-01, TEL-07 | 0001 | — | [3 mục](plans/m1-contract-v01/JOURNAL.md) |

## M1

| id | Ngày | Loại | Kết cục | Tầng | Test ID | Đã nâng thành | Tiêu đề |
|---|---|---|---|---|---|---|---|
| [S0011](entries/2026-08-25T193404Z-S0011-risky-cd-cusersanhnd0904workspacemechops-bash-mo.md) | 2026-08-25 | risky | reverted | infra | — | record-risky.sh: bo gia tri --why/--title/--promoted/-m... ; ma tran 24 ca | cd /c/Users/AnhND0904/workspace/MechOps ; bash ./mo steer close S0010 |
| [S0010](entries/2026-08-25T193137Z-S0010-risky-cd-cusersanhnd0904workspacemechops-git-add.md) | 2026-08-25 | risky | reverted | infra | — | record-risky.sh: scan=${cmd%%<<*} + _lib.sh json_str xu ly dau escape; ma tran 20 ca trong scratchpad | cd /c/Users/AnhND0904/workspace/MechOps ; git add -A ; git commit -F - |
| [S0009](entries/2026-08-25T191339Z-S0009-decision-contract-noi-plan-vao-specs-bang-thu-may-k.md) | 2026-08-25 | decision | kept | specs | — | tools/checks/contract_touch.py + buoc CI 'specs/ doi phai co plan khai truoc' | contract: noi plan vao specs bang thu may kiem duoc |
| [S0008](entries/2026-08-25T184817Z-S0008-decision-bo-sung-format-quyet-dinh-dong-bo-nhieu-nh.md) | 2026-08-25 | decision | kept | flow | — | trace.py: enum + decision bat buoc; next.py: pha CAN NGUOI QUYET; pr.yml: chot chan .steering khong lech | Bo sung format quyet dinh, dong bo nhieu nhanh, va triage plan treo |
| [S0007](entries/2026-08-25T182903Z-S0007-wrong-xoa-plan-m1-provisioning-mot-phien-plan-bi.md) | 2026-08-25 | wrong | kept | flow | — | ./mo steer plan abandon + trace: supersedes phai tro plan co that + CLAUDE.md cam xoa thu muc plan | Xoa plan m1-provisioning — mot phien plan bien mat khong dau vet |
| [S0006](entries/2026-08-25T182805Z-S0006-risky-cd-cusersanhnd0904workspacemechops-docker.md) | 2026-08-25 | risky | kept | infra | — | none | cd /c/Users/AnhND0904/workspace/MechOps ; docker compose -f docker-com |
| [S0005](entries/2026-08-25T182714Z-S0005-risky-cd-cusersanhnd0904workspacemechops-docker.md) | 2026-08-25 | risky | kept | infra | — | none — test trong ban sao, khong co gi de nang len | cd /c/Users/AnhND0904/workspace/MechOps ; docker compose -f docker-com |
| [S0004](entries/2026-08-25T181248Z-S0004-decision-ten-file-steering-gan-moc-thoi-gian-utc-o.md) | 2026-08-25 | decision | kept | flow | — | trace.py: moc trong ten file phai khop date: — CI do neu doi ten tay | Ten file steering gan moc thoi gian UTC o dau |
| [S0003](entries/2026-08-23T085925Z-S0003-risky-cd-cusersanhnd0904workspacemechopsnrm--rf.md) | 2026-08-23 | risky | reverted | infra | — | none — tracker da co hook chan ghi tay, day chi la don du lieu gia lap | cd /c/Users/AnhND0904/workspace/MechOps/nrm -rf docs/evidence/ci/2026- |
| [S0002](entries/2026-08-23T063717Z-S0002-discovery-4-skill-co-frontmatter-yaml-khong-hop-le-m.md) | 2026-08-23 | discovery | kept | flow | — | trace.py check_frontmatter() — CI bat thay vi dua vao may man | 4 skill co frontmatter YAML khong hop le ma van chay |
| [S0001](entries/2026-08-23T063715Z-S0001-wrong-golangci-lint-chay-duoc-voi-trong-gowork.md) | 2026-08-23 | wrong | reverted | infra | — | none — da co chu thich canh GO_PKGS trong Makefile:8 | golangci-lint chay duoc voi ./... trong go.work |
