#!/usr/bin/env python3
"""next.py — "tôi đang ở đâu, bước tiếp là gì".

Trạng thái để trả lời câu đó đã nằm sẵn ở dạng máy đọc được: tracker (milestone
đang mở, ID ⬜ đầu tiên), `.steering/plans/*/` (status + chỗ chưa điền),
`.steering/entries/` (mục còn `open`), git (nhánh, file chưa commit). Trước file
này không có gì tổng hợp lại, nên người và agent phải tự nhớ 8 cửa vào.

Skill `/dev` chạy lệnh này rồi làm theo. In cả **căn cứ** của kết luận — chẩn
đoán sai thì phải nhìn thấy được, không được sai im lặng.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANS = os.path.join(ROOT, ".steering", "plans")
ENTRIES = os.path.join(ROOT, ".steering", "entries")
STATUS_JSON = os.path.join(ROOT, "docs", "test-status.json")

sys.path.insert(0, os.path.join(ROOT, "tools", "testtrack"))
from track import CATALOG, milestone_num, milestone_of  # noqa: E402

# Dấu hiệu "chỗ này chưa ai điền" — template sinh ra đều dùng dạng <...>.
PLACEHOLDER = re.compile(r"<(điền|viết|liệt kê|mô tả|state|quan sát|file|câu hỏi|ID)")


def sh(*a, default=""):
    try:
        r = subprocess.run(a, capture_output=True, text=True, cwd=ROOT, timeout=15)
        return r.stdout.strip() if r.returncode == 0 else default
    except Exception:
        return default


def fm_of(path):
    if not os.path.exists(path):
        return {}
    t = open(path, encoding="utf-8").read()
    if not t.startswith("---") or "\n---\n" not in t:
        return {}
    fm = {}
    for line in t.split("\n---\n", 1)[0].lstrip("-\n").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm


def body_of(path):
    if not os.path.exists(path):
        return ""
    t = open(path, encoding="utf-8").read()
    return t.split("\n---\n", 1)[-1]


def tracker():
    if not os.path.exists(STATUS_JSON):
        return None, None, 0, 0
    tests = json.load(open(STATUS_JSON, encoding="utf-8"))["tests"]
    pending = [t for t in CATALOG if tests[t]["status"] != "pass"]
    if not pending:
        return None, None, len(CATALOG), len(CATALOG)
    n = min(milestone_num(milestone_of(t)) for t in pending)
    ids = [t for t in CATALOG if milestone_num(milestone_of(t)) == n]
    nxt = next((i for i in ids if tests[i]["status"] != "pass"), None)
    done = sum(1 for i in ids if tests[i]["status"] == "pass")
    return n, nxt, done, len(ids)


def plans():
    out = []
    if not os.path.isdir(PLANS):
        return out
    for name in sorted(os.listdir(PLANS)):
        d = os.path.join(PLANS, name)
        if not os.path.isdir(d):
            continue
        fm = fm_of(os.path.join(d, "spec.md"))
        st = {k: fm_of(os.path.join(d, f"{k}.md")).get("status", "?")
              for k in ("spec", "clarify", "plan", "testcases", "tasks")}
        out.append({
            "name": name,
            "milestone": fm.get("milestone", "?"),
            "st": st,
            # Cổng chốt là sự thật; placeholder chỉ là gợi ý "còn chỗ trống".
            # Trước đây next.py suy từ placeholder — đoán, không phải đọc.
            "frozen": all(v == "frozen" for v in
                          (st["spec"], st["plan"], st["testcases"], st["tasks"])),
            "ready": all(st[k] in ("locked", "frozen")
                         for k in ("spec", "plan", "testcases", "tasks")),
            "todo": {k: bool(PLACEHOLDER.search(body_of(os.path.join(d, f"{k}.md"))))
                     for k in ("spec", "clarify", "plan", "testcases", "tasks")},
        })
    return out


def open_entries():
    if not os.path.isdir(ENTRIES):
        return []
    return [fm_of(os.path.join(ENTRIES, n)) for n in sorted(os.listdir(ENTRIES))
            if n.endswith(".md") and fm_of(os.path.join(ENTRIES, n)).get("outcome") == "open"]


def decide():
    """Trả về (nhãn giai đoạn, lệnh tiếp theo, [căn cứ])."""
    ms, nxt, done, total = tracker()
    ps = plans()
    opened = open_entries()
    branch = sh("git", "rev-parse", "--abbrev-ref", "HEAD", default="?")
    dirty = len(sh("git", "status", "--porcelain").splitlines())
    why = [f"milestone đang mở M{ms}" if ms else "toàn bộ catalog đã xanh",
           f"nhánh {branch}, {dirty} file chưa commit",
           f"{len(ps)} plan, {len(opened)} mục nhật ký còn open"]

    if opened:
        ids = ", ".join(e.get("id", "?") for e in opened)
        return ("NỢ NHẬT KÝ", f"./mo steer close {opened[-1].get('id')} "
                "--outcome kept|reverted --why \"...\" --promoted \"...\"",
                why + [f"mục {ids} chưa đóng — không biết chuyện gì đã xảy ra"])

    if ms is None:
        return ("XONG", "không còn việc — mở milestone mới hoặc rà lại catalog", why)

    active = [p for p in ps if not p["frozen"] and p["milestone"] == f"M{ms}"]
    if not active:
        same = [p for p in ps if p["milestone"] == f"M{ms}"]
        note = (f"mọi plan của M{ms} đã frozen") if same else f"chưa có plan nào cho M{ms}"
        return ("VÒNG NGOÀI — chưa có plan",
                f'./mo steer plan new m{ms}-<ten> --milestone M{ms} --covers "{nxt}" '
                '--adr <NNNN> --requirements "docs/product/..."',
                why + [note, "rồi chạy /feature"])

    p = active[0]
    d = f".steering/plans/{p['name']}"
    st, todo = p["st"], p["todo"]
    gates = " ".join(f"{k}={st[k]}" for k in ("spec", "clarify", "plan", "testcases", "tasks"))
    why = why + [f"plan {p['name']}: {gates}"]

    if st["spec"] == "draft" and todo["spec"]:
        return ("VÒNG NGOÀI — specify", f"/feature — điền {d}/spec.md",
                why + [f"{d}/spec.md còn chỗ chưa điền"])
    if st["clarify"] == "open":
        return ("GATE NGƯỜI — clarify", f"DỪNG. Founder trả lời trong {d}/clarify.md",
                why + ["clarify chưa `answered` — agent KHÔNG trả lời thay (constitution #9)",
                       f"founder trả lời xong: ./mo steer plan lock {p['name']} spec"])
    if st["spec"] == "draft":
        return ("VÒNG NGOÀI — chốt spec", f"./mo steer plan lock {p['name']} spec", why)
    if st["plan"] == "draft":
        return ("VÒNG NGOÀI — tech-plan", f"/tech-plan {p['name']}",
                why + [f"điền {d}/plan.md rồi: ./mo steer plan lock {p['name']} plan"])
    if st["testcases"] == "draft":
        return ("VÒNG NGOÀI — testcases", f"điền {d}/testcases.md",
                why + ["mỗi ID trong covers phải có một mục `## <ID>`",
                       f"rồi: ./mo steer plan lock {p['name']} testcases"])
    if st["tasks"] == "draft":
        return ("VÒNG NGOÀI — tasks", f"/feature — bẻ task trong {d}/tasks.md",
                why + ["mỗi task ≥1 test ID, ID phải nằm trong covers",
                       f"rồi: ./mo steer plan lock {p['name']} tasks"])

    on_feat = branch.startswith("feat/")

    # Sửa trên main là NGOÀI vòng lặp, không phải giữa nó: repo quy định
    # 1 phiên = 1 task = 1 nhánh feat/. Gọi nhầm thành "đang làm task" sẽ khiến
    # agent đi thẳng tới /audit rồi commit vào main.
    if dirty > 0 and not on_feat:
        return ("NGOÀI VÒNG LẶP — đang sửa trên " + branch,
                f"commit việc đang dở, rồi: git switch -c feat/{(nxt or 'xxx').lower()}-<mô-tả>",
                why + [f"{dirty} file chưa commit nhưng không ở nhánh feat/",
                       "1 phiên = 1 task = 1 nhánh (CLAUDE.md)",
                       "commit cần dòng `Implements: <ID>` hoặc `Implements: none`"])

    if dirty == 0 and not on_feat:
        return ("VÒNG TRONG — bắt đầu task", f"/task {nxt}",
                why + [f"plan {p['name']} đã đủ bốn file",
                       "chạy /spec-analyze trước nếu vừa sửa spec/plan/tasks",
                       f"tách nhánh: git switch -c feat/{(nxt or '').lower()}-<mô-tả>"])

    if dirty > 0:
        return ("VÒNG TRONG — đang làm", "./mo verify  →  /audit  →  commit",
                why + [f"{dirty} file chưa commit trên nhánh {branch}",
                       "vòng lặp: ĐỎ (chứng minh) → XANH (tối thiểu) → GỌN (refactor)",
                       "đỏ không rõ vì sao → skill troubleshoot"])

    return ("VÒNG TRONG — sẵn sàng mở PR", "/pr",
            why + ["nhánh feat/* đã sạch, không còn thay đổi treo"])


def main():
    phase, cmd, why = decide()
    print(f"\n  ▸ ĐANG Ở: {phase}")
    print(f"  ▸ BƯỚC TIẾP: {cmd}\n")
    print("  Căn cứ:")
    for w in why:
        print(f"    · {w}")
    print()


if __name__ == "__main__":
    main()
