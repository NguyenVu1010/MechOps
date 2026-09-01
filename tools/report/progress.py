#!/usr/bin/env python3
"""progress.py — sinh docs/PROGRESS.md và cache một dòng cho statusline.

test-status.md trả lời "test nào xanh". File này trả lời câu người thật sự hỏi:
*còn bao xa, đi nhanh chậm thế nào, tuần tới làm gì.* Cùng một dữ liệu, khác câu hỏi.

Nguồn duy nhất là docs/test-status.json (do track.py ghi) — script này KHÔNG bao giờ
ghi vào tracker, chỉ đọc.

    progress.py                          # sinh docs/PROGRESS.md
    progress.py --cache .claude/cache/progress.txt --quiet
"""
import argparse
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "testtrack"))
from track import CATALOG, MILESTONE, milestone_of, milestone_num  # noqa: E402

STATUS_JSON = os.path.join(ROOT, "docs", "test-status.json")
OUT_MD = os.path.join(ROOT, "docs", "PROGRESS.md")
WEEKS_BACK = 8


def load():
    if not os.path.exists(STATUS_JSON):
        sys.exit("chưa có docs/test-status.json — chạy ./mo verify trước.")
    with open(STATUS_JSON, encoding="utf-8") as f:
        st = json.load(f)
    return st["tests"], st.get("updated") or "?"


def bar(done, total, width=20):
    if total == 0:
        return ""
    filled = round(width * done / total)
    return "█" * filled + "░" * (width - filled)


def by_milestone(tests):
    """{1: {'label': 'M1', 'ids': [...]}} — gom theo số milestone bắt đầu."""
    out = {}
    for tid in CATALOG:
        n = milestone_num(milestone_of(tid))
        out.setdefault(n, {"labels": set(), "ids": []})
        out[n]["labels"].add(milestone_of(tid))
        out[n]["ids"].append(tid)
    return dict(sorted(out.items()))


def iso_week(ts):
    d = dt.datetime.strptime(ts[:10], "%Y-%m-%d").date()
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def velocity(tests):
    """Số test chuyển xanh theo tuần ISO, suy từ lastRun của các test đang pass."""
    counts = {}
    for t in tests.values():
        if t["status"] == "pass" and t.get("lastRun"):
            counts[iso_week(t["lastRun"])] = counts.get(iso_week(t["lastRun"]), 0) + 1
    return counts


def render(tests, updated):
    total = len(CATALOG)
    done = sum(1 for t in CATALOG if tests[t]["status"] == "pass")
    groups = by_milestone(tests)

    open_n = next((n for n, g in groups.items()
                   if any(tests[i]["status"] != "pass" for i in g["ids"])), None)

    L = [
        "# MechOps — Tiến độ",
        "",
        "> ⚙️ Sinh bởi `tools/report/progress.py` từ `docs/test-status.json` — **không sửa tay**.",
        # Lấy mốc TỪ tracker, không phải giờ hiện tại. Đóng dấu "bây giờ" thì mỗi
        # lần `./mo status` lại sinh một diff chỉ khác timestamp — không mang nội
        # dung nào, mà vẫn nằm chình ình trong `git status` để người ta commit theo
        # phản xạ. File này là hàm thuần của test-status.json, nên nó phải đổi đúng
        # lúc tracker đổi, không sớm hơn. (track.py cũng vừa được sửa cùng lý do.)
        f"> Cập nhật: {updated} · "
        f"**{done}/{total}** ({100 * done // total}%)",
        "",
    ]

    # --- Việc tiếp theo: thứ người mở file này để tìm ---
    L += ["## Việc tiếp theo", ""]
    if open_n is None:
        L += ["Toàn bộ catalog đã xanh.", ""]
    else:
        nxt = [i for i in groups[open_n]["ids"] if tests[i]["status"] != "pass"][:5]
        L += [f"Milestone đang mở: **M{open_n}**", "",
              "| ID | Tầng | Mô tả |", "|---|---|---|"]
        for i in nxt:
            L.append(f"| `{i}` | [{tests[i]['tier']}] | {tests[i]['desc']} |")
        L += ["",
              "> Test [H] chỉ người tick (`./mo hw-test`). Test [U]/[I] là việc của agent.",
              ""]

    # --- Burndown ---
    L += ["## Burndown theo milestone", "",
          "| Milestone | Xong | Tổng | | Nhóm |", "|---|---|---|---|---|"]
    for n, g in groups.items():
        gdone = sum(1 for i in g["ids"] if tests[i]["status"] == "pass")
        prefixes = sorted({i.split("-")[0] for i in g["ids"]})
        mark = " ←" if n == open_n else ""
        L.append(f"| **M{n}**{mark} | {gdone} | {len(g['ids'])} | `{bar(gdone, len(g['ids']))}` "
                 f"| {', '.join(prefixes)} |")
    L.append("")

    # --- Velocity ---
    v = velocity(tests)
    L += ["## Nhịp độ (test chuyển ✅ mỗi tuần)", ""]
    if not v:
        L += ["Chưa có test nào xanh — chưa đo được nhịp độ.", ""]
    else:
        weeks = sorted(v)[-WEEKS_BACK:]
        L += ["| Tuần | Số test ✅ | |", "|---|---|---|"]
        for w in weeks:
            L.append(f"| {w} | {v[w]} | {'▇' * v[w]} |")
        remain = total - done
        avg = sum(v[w] for w in weeks) / len(weeks)
        eta = f"~{remain / avg:.0f} tuần nữa" if avg > 0 else "chưa ước lượng được"
        L += ["", f"Trung bình {avg:.1f} test/tuần · còn {remain} test · **{eta}** theo nhịp hiện tại.",
              "", "> Ước lượng thô: [H] cần phần cứng thật nên không đi theo nhịp [U]/[I].", ""]

    # --- Việc đang hỏng ---
    bad = [(i, tests[i]) for i in CATALOG if tests[i]["status"] in ("fail", "stale")]
    L += ["## Đang đỏ / cũ", ""]
    if not bad:
        L += ["Không có test ❌ hay ⚠️.", ""]
    else:
        L += ["| ID | Trạng thái | Lần cuối | Evidence |", "|---|---|---|---|"]
        for i, t in bad:
            ev = f"[log]({t['evidence']})" if t.get("evidence") else "—"
            L.append(f"| `{i}` | {t['status']} | {(t.get('lastRun') or '—')[:10]} | {ev} |")
        L.append("")

    if open_n is None:
        summary = (done, total, None, None, 0, 0)
    else:
        ids = groups[open_n]["ids"]
        summary = (done, total, open_n,
                   next((i for i in ids if tests[i]["status"] != "pass"), None),
                   sum(1 for i in ids if tests[i]["status"] == "pass"), len(ids))
    return "\n".join(L) + "\n", summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cache", help="ghi một dòng tóm tắt cho statusline")
    p.add_argument("--quiet", action="store_true")
    a = p.parse_args()

    tests, updated = load()
    md, (done, total, open_n, nxt, mdone, mtotal) = render(tests, updated)

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(md)

    if a.cache:
        os.makedirs(os.path.dirname(a.cache), exist_ok=True)
        # Statusline chỉ có một dòng: milestone đang mở trước, tổng sau — thứ tự
        # theo mức độ ảnh hưởng tới việc đang làm.
        line = (f"M{open_n} {mdone}/{mtotal} · next {nxt} · tổng {done}/{total}"
                if open_n else f"toàn bộ {total} test xanh")
        with open(a.cache, "w", encoding="utf-8") as f:
            f.write(line + "\n")

    if not a.quiet:
        print(f"progress: docs/PROGRESS.md · {done}/{total} · "
              f"{'milestone M%d, tiếp theo %s' % (open_n, nxt) if open_n else 'tất cả xanh'}")


if __name__ == "__main__":
    main()
