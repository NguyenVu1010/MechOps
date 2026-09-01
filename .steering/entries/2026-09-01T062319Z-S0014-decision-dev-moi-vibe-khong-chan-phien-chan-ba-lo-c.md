---
id: S0014
date: 2026-09-01T06:23:19Z
kind: decision
outcome: kept
title: "Dev moi vibe: khong chan phien, chan ba lo cu the"
decision: "Khong dat rao can nao truoc phien vibe. Thay vao do: session-start tu bat git hook, va ba luat chi-nam-trong-van-ban (conflict marker, t.Skip, xoa plan) tro thanh chot chan may."
reversible: yes
deciders: agent+founder
revisit: 
area: flow
plan: 
milestone: M1
test_ids: []
supersedes: []
branch: "develop"
commit: f6a5fa6
evidence: "docs/evidence/ci/2026-07-14T193011Z-544e2a4"
promoted_to: "Makefile check-merge + trace.py check_no_skip + trace.py check_deleted_plans + session-start.sh tu bat hook"
source: agent
---

# S0014 · Dev moi vibe: khong chan phien, chan ba lo cu the

## Vì sao đụng tới
Cau hoi: dev moi chua hieu quy trinh, mo phien va vibe thuan thi he thong co sao khong. Soi lai ba lop bao ve.

## Tin rằng
Tin rang rui ro den tu viec vibe. Sai: lop Claude Code (.claude/settings.json) di theo repo nen tu chay ngay sau clone — CLAUDE.md vao context, guard-tracker chan cung. Rui ro that den tu core.hooksPath la config LOCAL nen khong di theo clone, va tu do vang mat IM LANG.

## Đã cân nhắc
- Chan phien vibe hoac bat doc tai lieu truoc: khong giai quyet goc (dev ky luat quen hooks-install cung hong y het) va mat dung thu dang bao ve tot nhat
- Chi canh bao thay vi tu bat: dung nguoi can nhat la nguoi se luot qua

## Đã làm
- session-start.sh tu dat core.hooksPath + merge.ours.driver, canh bao len dau context
- Makefile check-merge quet conflict marker, verify phu thuoc vao no
- trace.py check_no_skip
- trace.py check_deleted_plans

## Bằng chứng
4 ca am chay that: marker trong file tracked -> exit khac 0; ======= cua tieu de setext KHONG bao oan; t.Skip -> trace exit 1, cung dong trong comment -> exit 0; move plan di -> exit 1, tra lai -> exit 0. Go ca hai config roi chay session-start -> tu dat lai, lan hai im lang.

## Kết luận
**kept** — Founder chot: lam ca bon. Branch protection tren develop van con no — do la cai dat GitHub, khong phai code.

_Đóng 2026-09-01T06:23:20Z · commit `f6a5fa6`_

## Đã nâng thành
Makefile check-merge + trace.py check_no_skip + trace.py check_deleted_plans + session-start.sh tu bat hook
