#!/usr/bin/env python3
"""Cưỡng chế dòng `Implements:` trong commit message.

Quy tắc catalog #1: "Mỗi PR khai báo ID test nó ảnh hưởng". Trước đây quy tắc này
chỉ nằm trong CLAUDE.md — tức là chỉ đúng khi agent nhớ. Script này làm nó thành
điều kiện để commit tồn tại.

Dùng:
    commit_msg.py .git/COMMIT_EDITMSG        # git hook commit-msg
    commit_msg.py --range origin/main..HEAD  # CI, quét mọi commit của PR

Commit không gắn test ID (docs, chore, dựng flow) vẫn hợp lệ, nhưng phải khai
TƯỜNG MINH `Implements: none`. Im lặng không được tính là "không liên quan".
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "testtrack"))
from track import CATALOG  # noqa: E402  (nguồn sự thật duy nhất của danh sách ID)

IMPLEMENTS_RE = re.compile(r"^Implements:\s*(.+?)\s*$", re.MULTILINE)
ID_RE = re.compile(r"^(PRV|ACL|TEL|PRB|OTA|ALT|TRM|WLB|INS|LOD)-\d{2}$")


def check(msg, label):
    """Trả về danh sách lỗi (rỗng = hợp lệ)."""
    errs = []
    subject = msg.strip().splitlines()[0] if msg.strip() else ""

    if subject.startswith(("Merge ", "Revert ")):
        return []  # commit do git sinh, không phải người khai

    found = IMPLEMENTS_RE.findall(msg)
    if not found:
        errs.append(
            "thiếu dòng `Implements: <ID>`.\n"
            "    Ví dụ: Implements: OTA-07, OTA-08\n"
            "    Commit không gắn test ID phải khai rõ: Implements: none"
        )
        return [f"{label}: {e}" for e in errs]

    if len(found) > 1:
        errs.append("có nhiều hơn một dòng `Implements:` — gộp lại thành một.")

    raw = found[0]
    if raw.strip().lower() == "none":
        return [f"{label}: {e}" for e in errs]

    ids = [p.strip() for p in raw.split(",") if p.strip()]
    if not ids:
        errs.append("dòng `Implements:` rỗng.")
    for tid in ids:
        if not ID_RE.match(tid):
            errs.append(f"ID sai định dạng: {tid!r} (đúng: OTA-07)")
        elif tid not in CATALOG:
            errs.append(
                f"ID {tid} không có trong catalog. "
                "Bug mới thì THÊM ID vào docs/product/05-test-catalog.md + CATALOG "
                "của track.py trước (quy tắc catalog #3), rồi mới commit."
            )
    return [f"{label}: {e}" for e in errs]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file", nargs="?", help="file chứa commit message (git hook truyền vào)")
    p.add_argument("--range", dest="rng", help="dải commit để quét, ví dụ origin/main..HEAD")
    a = p.parse_args()

    errs = []
    if a.rng:
        out = subprocess.run(
            ["git", "log", "--format=%H", a.rng], capture_output=True, text=True, cwd=ROOT
        )
        if out.returncode != 0:
            print(f"không đọc được dải {a.rng}: {out.stderr.strip()}", file=sys.stderr)
            return 1
        shas = [s for s in out.stdout.split() if s]
        if not shas:
            print(f"commit-msg: không có commit nào trong {a.rng} — bỏ qua.")
            return 0
        for sha in shas:
            body = subprocess.run(
                ["git", "log", "-1", "--format=%B", sha], capture_output=True, text=True, cwd=ROOT
            ).stdout
            errs += check(body, sha[:7])
    elif a.file:
        with open(a.file, encoding="utf-8") as f:
            errs += check(f.read(), "commit")
    else:
        p.error("cần <file> hoặc --range")

    if errs:
        print("\n\033[31mCommit bị từ chối:\033[0m", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        print(
            "\n  Vì sao: docs/product/05-test-catalog.md quy tắc #1 — mỗi thay đổi "
            "phải nói rõ nó chạm test ID nào. Đây là sợi chỉ nối commit với evidence.",
            file=sys.stderr,
        )
        return 1

    print("commit-msg: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
