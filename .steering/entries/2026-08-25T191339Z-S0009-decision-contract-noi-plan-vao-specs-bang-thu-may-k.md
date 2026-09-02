---
id: S0009
date: 2026-08-25T19:13:39Z
kind: decision
outcome: kept
title: "contract: noi plan vao specs bang thu may kiem duoc"
decision: "spec.md khai contract: [file/thu muc trong specs/]; CI doi chieu diff specs/ voi danh sach do"
reversible: yes
deciders: agent+founder
revisit: 
area: specs
plan: m1-contract-v01
milestone: M1
test_ids: []
supersedes: []
branch: "feat/ai-flow"
commit: 2e7338f
evidence: "docs/evidence/ci/2026-07-14T193011Z-544e2a4"
promoted_to: "tools/checks/contract_touch.py + buoc CI 'specs/ doi phai co plan khai truoc'"
source: agent
---

# S0009 · contract: noi plan vao specs bang thu may kiem duoc

## Vì sao đụng tới
plan.md muc 1 'Delta hop dong' la van xuoi — khong gi kiem duoc rang file specs/ vua doi da tung nam trong ke hoach.

## Tin rằng
Tin rang skill spec-analyze nhac doi chieu la du. Do la phan doan cua agent, khong phai chot chan: agent quen mot lan la mot field vao hop dong ma khong ai duyet.

## Đã cân nhắc
- Chan moi thay doi specs/ tru khi commit khai Contract: trailer — bo vi trailer khong noi duoc scope cua ca feature
- Bat CI do ngay khi chua plan nao khai — bo vi M0 dang dung specs/ tu dau, chot chan do oan se bi tat truoc khi kip co ich (nen cong TU BAT khi co plan dau tien khai)

## Đã làm
- steer.py: --contract o plan new + plan contract --add/--list, locked thi bat buoc --why va sinh nhat ky
- trace.py: duong dan phai trong specs/, thu muc phai ton tai
- tools/checks/contract_touch.py + ./mo check-contract
- pr.yml: buoc 'specs/ doi phai co plan khai truoc'
- m1-contract-v01 khai 3 muc

## Bằng chứng
Test: doi specs/schemas/telemetry.schema.json (khop prefix specs/schemas/) -> OK; doi specs/probe-api.md chua khai -> exit 1; khai them roi chay lai -> exit 0. Locked ma thieu --why -> tu choi. protocol/topics.go -> tu choi. specs/khong-co/ -> tu choi.

## Kết luận
**kept** — Chot chan chay dung hai chieu, cong tu bat nen khong do oan trong M0.

_Đóng 2026-08-25T19:13:40Z · commit `2e7338f`_

## Đã nâng thành
tools/checks/contract_touch.py + buoc CI 'specs/ doi phai co plan khai truoc'
