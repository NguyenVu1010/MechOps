---
id: S0004
date: 2026-08-25T18:12:48Z
kind: decision
outcome: kept
title: "Ten file steering gan moc thoi gian UTC o dau"
decision: "Ten file steering gan moc thoi gian UTC o dau"
reversible: yes
deciders: agent
revisit:
area: flow
plan: 
milestone: M1
test_ids: []
supersedes: []
branch: "feat/ai-flow"
commit: 2e7338f
evidence: "docs/evidence/ci/2026-07-14T193011Z-544e2a4"
promoted_to: "trace.py: moc trong ten file phai khop date: — CI do neu doi ten tay"
source: agent
---

# S0004 · Ten file steering gan moc thoi gian UTC o dau

## Vì sao đụng tới
Doc ls .steering/entries/ khong biet mot muc xay ra luc nao ma khong mo file; thu tu file tren dia la thu tu id, khong phai thu tu su viec.

## Tin rằng
Tuong rang id tang dan la du de biet thu tu. Du de SAP THU TU, khong du de biet KHOANG CACH: S0002 va S0003 cach nhau 2 gio hay 2 tuan la hai cau chuyen khac nhau.

## Đã làm
- steer.py: mot lan goi dong ho cho ca ten file lan date:
- trace.py: moc trong ten file phai khop date:
- git mv 3 muc cu, moc lay tu date: cua chinh muc do
- .steering/README.md: so do ten file

## Bằng chứng
Dang moc y het docs/evidence/ci/ (2026-07-14T135207Z-e798570) — mot quy uoc cho moi thu co dau thoi gian trong repo. Test am: doi ten sai moc -> ./mo trace exit 2; bo moc -> exit 2.

## Kết luận
**kept** — Da doi format va di tru 3 muc cu; trace bat ca hai kieu sai ten (lech moc, thieu moc) bang exit 2.

_Đóng 2026-08-25T18:12:58Z · commit `2e7338f`_

## Đã nâng thành
trace.py: moc trong ten file phai khop date: — CI do neu doi ten tay
