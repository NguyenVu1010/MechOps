---
id: S0008
date: 2026-08-25T18:48:17Z
kind: decision
outcome: kept
title: "Bo sung format quyet dinh, dong bo nhieu nhanh, va triage plan treo"
decision: "moi ban tin mang decision/reversible/deciders/revisit + muc Da can nhac; plan treo do ./mo steer plan triage hoi va chi tra loi bang keep/abandon"
reversible: costly
deciders: agent+founder
revisit: 
area: flow
plan: 
milestone: M1
test_ids: []
supersedes: []
branch: "feat/ai-flow"
commit: 2e7338f
evidence: "docs/evidence/ci/2026-07-14T193011Z-544e2a4"
promoted_to: "trace.py: enum + decision bat buoc; next.py: pha CAN NGUOI QUYET; pr.yml: chot chan .steering khong lech"
source: agent
---

# S0008 · Bo sung format quyet dinh, dong bo nhieu nhanh, va triage plan treo

## Vì sao đụng tới
Founder yeu cau: quan ly triet de tung quyet dinh, xu ly dong bo giua cac nhanh khi dev moi, va hook phai hoi khi plan bi lac hoac bi bo qua.

## Tin rằng
Tin rang giu du plan la du de truy vet. Sai o hai cho: (1) plan khong bi xoa van co the im lang troi khoi tam nhin, khong ai dong khong ai lam; (2) id cap theo max+1 trong cay lam viec se trung khi hai nhanh chay song song, va id la thu supersedes tro toi.

## Đã cân nhắc
- ID dang ULID/hash de khoi trung nhanh — bo vi mat kha nang trich dan 'xem S0007' nhu ADR
- Khong commit file may sinh vao git — bo vi mat ban doc duoc luc review PR
- merge=union cho INDEX.md — bo vi noi hai nua bang markdown ra mot bang sai ma im lang
- triage chan CI (--strict) — bo vi 'plan im lang 14 ngay' la viec nguoi quyet, chan merge thi hook se bi tat

## Đã làm
- steer.py: 4 field + muc Da can nhac; next_id quet git log --all; renumber; plan keep; triage; HISTORY them dap an clarify
- trace.py: kiem enum + decision bat buoc
- next.py: pha CAN NGUOI QUYET dung truoc moi viec moi
- .gitattributes merge=ours + post-merge + post-checkout
- pr.yml: chot chan .steering khong lech

## Bằng chứng
Merge that hai nhanh (scratchpad/mt2): 0 conflict marker o INDEX.md va PROGRESS.md, ca 2 muc nhat ky ve du. Trung id -> trace exit 1 -> renumber -> exit 0. Triage bat 3/3 dieu kien (mo coi nhanh, bi vuot, treo gate 55 ngay); plan keep lam im. 3 test am cho format: thieu --decision, reversible sai, revisit sai dinh dang.

## Kết luận
**kept** — Da di tru 7 muc cu sang format moi, trace sach, merge that khong conflict.

_Đóng 2026-08-25T18:48:19Z · commit `2e7338f`_

## Đã nâng thành
trace.py: enum + decision bat buoc; next.py: pha CAN NGUOI QUYET; pr.yml: chot chan .steering khong lech
