#!/usr/bin/env python3
"""pr_digest.py — dựng phần thân PR mà founder thật sự cần đọc.

docs/DEVELOPMENT.md hứa founder review một PR trong 5 phút bằng cách nhìn 3 thứ:
tick mới, một link evidence, kết luận hai kiểm toán viên. Trước đây PR không hiện
thứ nào trong ba thứ đó — người review phải tự đi đào. File này đào sẵn.

    pr_digest.py --base origin/main --head HEAD
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "testtrack"))
from track import CATALOG, milestone_of  # noqa: E402

IMPLEMENTS_RE = re.compile(r"^Implements:\s*(.+?)\s*$", re.MULTILINE)
ID_RE = re.compile(r"[A-Z]{3}-\d{2}")


def git(*args, allow_fail=False):
    r = subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        if allow_fail:
            return None
        sys.exit(f"git {' '.join(args)} lỗi: {r.stderr.strip()}")
    return r.stdout


def status_at(ref):
    """docs/test-status.json tại một ref. None nếu ref/file không tồn tại."""
    out = git("show", f"{ref}:docs/test-status.json", allow_fail=True)
    if out is None:
        return None
    try:
        return json.loads(out)["tests"]
    except (ValueError, KeyError):
        return None


def declared_ids(base, head):
    """ID khai trong dòng Implements: của mọi commit trong dải."""
    log = git("log", "--format=%B%x00", f"{base}..{head}", allow_fail=True) or ""
    ids = []
    for body in log.split("\x00"):
        for m in IMPLEMENTS_RE.findall(body):
            if m.strip().lower() == "none":
                continue
            ids += ID_RE.findall(m)
    return sorted(set(ids))


def changed(base, head, prefix):
    out = git("diff", "--name-status", f"{base}...{head}", "--", prefix, allow_fail=True) or ""
    return [tuple(l.split("\t", 1)) for l in out.strip().splitlines() if "\t" in l]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="origin/main")
    p.add_argument("--head", default="HEAD")
    a = p.parse_args()

    before, after = status_at(a.base), status_at(a.head)
    L = ["## 🤖 PR digest", "",
         "_Sinh bởi `tools/report/pr_digest.py`. Ba mục dưới đây là đúng ba thứ "
         "docs/DEVELOPMENT.md yêu cầu founder nhìn._", ""]

    # --- 1. Tick mới + evidence ---
    L += ["### 1. Test chuyển ✅ trong PR này", ""]
    newly = []
    if before and after:
        newly = [t for t in CATALOG
                 if after.get(t, {}).get("status") == "pass"
                 and before.get(t, {}).get("status") != "pass"]
    if not newly:
        L += ["Không có tick mới.", ""]
    else:
        L += ["| ID | Milestone | Tầng | Mô tả | Evidence |", "|---|---|---|---|---|"]
        for t in newly:
            e = after[t].get("evidence")
            L.append(f"| `{t}` | {milestone_of(t)} | [{after[t]['tier']}] | "
                     f"{after[t]['desc']} | {f'[raw log]({e})' if e else '**thiếu**'} |")
        L.append("")
        no_ev = [t for t in newly if not after[t].get("evidence")]
        if no_ev:
            L += [f"> ⛔ **{', '.join(no_ev)} xanh nhưng không có evidence** — "
                  "vi phạm constitution #2. Không merge cho tới khi giải thích được.", ""]

    # --- 2. Khai báo so với thực tế ---
    decl = declared_ids(a.base, a.head)
    L += ["### 2. ID khai trong commit so với ID thật sự xanh", ""]
    if not decl:
        L += ["Không commit nào khai `Implements:` với ID (chỉ `none`).", ""]
    else:
        L += [f"Khai: {', '.join(f'`{d}`' for d in decl)}", ""]
        gap = [d for d in decl if d not in newly and after and after.get(d, {}).get("status") != "pass"]
        if gap:
            L += [f"> ⚠️ Khai `{', '.join(gap)}` nhưng các ID này chưa xanh. "
                  "Hợp lệ nếu PR còn dở; không hợp lệ nếu PR tự nhận là xong.", ""]

    # --- 3. Contract và quyết định ---
    specs = changed(a.base, a.head, "specs")
    adrs = [c for c in changed(a.base, a.head, "docs/adr") if c[0] == "A"]
    L += ["### 3. Contract & quyết định", ""]
    if specs:
        L += ["**`specs/` đã đổi** — đọc kỹ, đây là hợp đồng (constitution #4):", ""]
        L += [f"- `{f}` ({'thêm' if s == 'A' else 'sửa' if s == 'M' else s})" for s, f in specs]
        L.append("")
    else:
        L += ["`specs/` không đổi.", ""]
    if adrs:
        L += ["**ADR mới:**", ""] + [f"- `{f}`" for _, f in adrs] + [""]

    # --- 4. Checklist người ---
    L += ["### 4. Còn lại cho người", "",
          "- [ ] Kết luận `spec-guardian`: PASS / FAIL (dán vào đây)",
          "- [ ] Kết luận `test-auditor`: PASS / FAIL (dán vào đây)",
          "- [ ] Đã mở **một** link evidence ở mục 1 và thấy log thật",
          "- [ ] Dependency mới (nếu có) đã có ADR — constitution #5, #6",
          ""]

    print("\n".join(L))


if __name__ == "__main__":
    main()
