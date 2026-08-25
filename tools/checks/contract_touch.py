#!/usr/bin/env python3
"""contract_touch.py — file `specs/` nào bị sửa mà không plan nào khai trước.

Hợp đồng là thứ code không được lệch (CLAUDE.md: "code lệch spec là bug của code").
Nhưng trước script này, `plan.md` mục 1 ("Delta hợp đồng") là **văn xuôi**: không
gì kiểm được rằng file hợp đồng vừa đổi đã từng nằm trong kế hoạch. Đó là đúng cách
spec-drift bắt đầu — một field thêm vào giữa lúc implement, không ai duyệt, và sáu
tháng sau không ai biết nó từ đâu ra.

`contract:` trong `.steering/plans/<x>/spec.md` khai trước; script này đối chiếu.

    python3 tools/checks/contract_touch.py --range origin/main..HEAD

**Cổng tự bật.** Chưa plan nào khai `contract:` thì thoát 0 kèm ghi chú — M0 đang
dựng `specs/` từ đầu, chặn lúc này thì chốt chặn bị tắt trước khi nó kịp có ích.
Có plan đầu tiên khai là cổng bắt đầu có hiệu lực.
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLANS = os.path.join(ROOT, ".steering", "plans")


def sh(*a):
    r = subprocess.run(a, capture_output=True, text=True, cwd=ROOT)
    return r.stdout if r.returncode == 0 else ""


def fm(path):
    if not os.path.exists(path):
        return {}
    t = open(path, encoding="utf-8").read()
    if not t.startswith("---") or "\n---\n" not in t:
        return {}
    out = {}
    for line in t.split("\n---\n", 1)[0].lstrip("-\n").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def declared():
    """{đường dẫn -> plan khai nó}. Plan `abandoned` không cho phép gì cả."""
    out = {}
    if not os.path.isdir(PLANS):
        return out
    for name in sorted(os.listdir(PLANS)):
        f = fm(os.path.join(PLANS, name, "spec.md"))
        if not f or f.get("closed_as") == "abandoned":
            continue
        for c in re.split(r"[,\s]+", f.get("contract", "").strip("[]")):
            if c:
                out.setdefault(c.replace("\\", "/"), []).append(name)
    return out


def trailers(rng):
    """`Contract: specs/... — lý do` trong bất kỳ commit nào của range.

    Cửa thứ hai, cho thay đổi hợp đồng KHÔNG thuộc feature nào: xoá phần scaffolding
    cũ, dọn sau một ADR, đổi tổ chức thư mục. Bắt những việc đó phải mượn một plan
    thì `contract:` của plan thành nói dối về scope của nó.

    Cửa này không im lặng: dòng trailer nằm trong `git log` vĩnh viễn, người duyệt
    PR đọc thấy, và nó buộc nêu lý do ngay cạnh đường dẫn.
    """
    out = []
    raw = sh("git", "log", "--format=%H%x1f%B%x1e", rng)
    for rec in raw.split("\x1e"):
        if "\x1f" not in rec:
            continue
        sha, msg = rec.split("\x1f", 1)
        for line in msg.splitlines():
            m = re.match(r"^\s*Contract:\s*(.+)$", line)
            if not m:
                continue
            for tok in re.findall(r"specs/[^\s,;]*", m.group(1)):
                out.append((sha.strip()[:7], tok.rstrip("*")))
    return out


def by_trailer(path, tr):
    for sha, tok in tr:
        if tok.endswith("/") and path.startswith(tok):
            return sha
        if path == tok:
            return sha
    return None


def authorized(path, decl):
    for d, plans in decl.items():
        if d.endswith("/") and path.startswith(d):
            return plans
        if path == d:
            return plans
    return None


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--range", default="origin/main..HEAD",
                   help="khoảng commit, mặc định origin/main..HEAD")
    a = p.parse_args()

    decl = declared()
    if not decl:
        print("contract: chưa plan nào khai `contract:` — bỏ qua "
              "(cổng tự bật khi có plan đầu tiên khai).")
        return 0

    changed = [l.strip().replace("\\", "/") for l in
               sh("git", "diff", "--name-only", a.range, "--", "specs").splitlines()
               if l.strip()]
    if not changed:
        print(f"contract: {a.range} không đụng specs/ — OK")
        return 0

    tr = trailers(a.range)
    bad = []
    for f in changed:
        who = authorized(f, decl)
        sha = None if who else by_trailer(f, tr)
        if who:
            print(f"  OK   {f}   ← plan {', '.join(who)}")
        elif sha:
            print(f"  OK   {f}   ← trailer Contract: ở {sha}")
        else:
            bad.append(f)

    if bad:
        print()
        for f in bad:
            print(f"LỖI: {f} đổi mà không plan nào khai trước trong `contract:`")
        print("\nCách xử lý — chọn một, đừng sửa lặng lẽ:")
        print("  1. Thuộc một feature  → ./mo steer plan contract <plan> "
              "--add <đường dẫn> --why \"...\"")
        print("  2. Feature mới        → ./mo steer plan new <tên> --milestone Mx "
              "--covers <ID> --contract <đường dẫn>")
        print("  3. Không thuộc feature nào (dọn dẹp, đổi tổ chức, sau một ADR) →")
        print("     thêm vào commit message dòng trailer, nêu lý do:")
        print(f"         Contract: {bad[0]} — <vì sao>")
        print("Đang khai: " + ", ".join(sorted(decl)))
        return 1

    print(f"contract: {len(changed)} file specs/ đổi, tất cả đã khai trước — OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
