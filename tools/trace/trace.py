#!/usr/bin/env python3
"""
trace.py — traceability check (Lớp 3, docs/product/06-spec-management.md).

Hai nhiệm vụ:
1. Mỗi test ID trong catalog phải xuất hiện ở >=1 file spec (dòng covers:)
   và >=1 file test Go (naming Test<ID bỏ gạch>_...). ID mồ côi = CẢNH BÁO.
   covers: trỏ tới ID không có trong catalog = LỖI (chặn typo).
2. Skill frontmatter `adr: [NNNN, ...]` — ADR không tồn tại hoặc đã
   superseded mà skill chưa cập nhật = LỖI (luật đồng bộ skill<->ADR).

Exit 0 nếu chỉ có cảnh báo; exit 1 nếu có lỗi.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "testtrack"))
from track import CATALOG  # một nguồn sự thật, không parse lại catalog md

SPEC_DIRS = ["specs", os.path.join("docs", "adr")]
SKILL_DIR = os.path.join(".claude", "skills")
ADR_DIR = os.path.join("docs", "adr")

COVERS_RE = re.compile(r'"?[Cc]overs"?\s*:\s*\[?\s*"?([A-Z]{3}-\d{2}(?:[",\s]+[A-Z]{3}-\d{2})*)', re.M)
ID_IN_LIST_RE = re.compile(r"[A-Z]{3}-\d{2}")
ADR_FM_RE = re.compile(r"^adr:\s*\[([0-9,\s]+)\]", re.M)


def walk_files(reldir, exts):
    base = os.path.join(ROOT, reldir)
    for dirpath, _, names in os.walk(base):
        if ".git" in dirpath:
            continue
        for n in names:
            if any(n.endswith(e) for e in exts):
                yield os.path.join(dirpath, n)


def collect_covers():
    """{ID: [file, ...]} từ mọi dòng covers: trong specs/ + docs/adr/."""
    found = {}
    for d in SPEC_DIRS:
        for path in walk_files(d, (".md", ".yaml", ".yml", ".json")):
            text = open(path, encoding="utf-8").read()
            rel = os.path.relpath(path, ROOT)
            for m in COVERS_RE.finditer(text):
                for tid in ID_IN_LIST_RE.findall(m.group(1)):
                    found.setdefault(tid, []).append(rel)
    return found


def collect_test_ids():
    """ID xuất hiện trong tên test Go: TestOTA07_... -> OTA-07."""
    ids = set()
    pat = re.compile(r"func\s+Test([A-Z]{3})(\d{2})\w*\(")
    for path in walk_files(".", ("_test.go",)):
        for m in pat.finditer(open(path, encoding="utf-8").read()):
            ids.add(f"{m.group(1)}-{m.group(2)}")
    return ids


def adr_status():
    """{NNNN: 'accepted'|'superseded'} từ dòng Status của mỗi ADR."""
    st = {}
    num_re = re.compile(r"^(\d{4})-")
    for name in os.listdir(os.path.join(ROOT, ADR_DIR)):
        m = num_re.match(name)
        if not m:
            continue
        text = open(os.path.join(ROOT, ADR_DIR, name), encoding="utf-8").read()
        sm = re.search(r"^- Status:\s*(.+)$", text, re.M)
        status = (sm.group(1).strip().lower() if sm else "")
        st[m.group(1)] = "superseded" if "superseded" in status else "accepted"
    return st


def main():
    errors, warns = [], []

    covers = collect_covers()
    test_ids = collect_test_ids()

    # covers: trỏ tới ID lạ = lỗi
    for tid, files in sorted(covers.items()):
        if tid not in CATALOG:
            errors.append(f"covers trỏ tới ID không có trong catalog: {tid} ({', '.join(files)})")

    # ID mồ côi = cảnh báo
    no_spec = [t for t in CATALOG if t not in covers]
    no_test = [t for t in CATALOG if t not in test_ids]
    if no_spec:
        warns.append(f"{len(no_spec)}/{len(CATALOG)} ID chưa có covers trong spec: {', '.join(sorted(no_spec)[:8])}{'…' if len(no_spec) > 8 else ''}")
    if no_test:
        warns.append(f"{len(no_test)}/{len(CATALOG)} ID chưa có test Go: {', '.join(sorted(no_test)[:8])}{'…' if len(no_test) > 8 else ''}")

    # skill <-> ADR
    statuses = adr_status()
    for path in walk_files(SKILL_DIR, ("SKILL.md",)):
        rel = os.path.relpath(path, ROOT)
        m = ADR_FM_RE.search(open(path, encoding="utf-8").read())
        if not m:
            continue
        for num in re.findall(r"\d{4}", m.group(1)):
            if num not in statuses:
                errors.append(f"{rel}: frontmatter adr trỏ tới ADR-{num} không tồn tại")
            elif statuses[num] == "superseded":
                errors.append(f"{rel}: adr {num} đã superseded — cập nhật skill cùng PR (luật trong .claude/skills/adr)")

    for w in warns:
        print(f"trace CẢNH BÁO: {w}")
    for e in errors:
        print(f"trace LỖI: {e}", file=sys.stderr)
    if errors:
        sys.exit(1)
    print(f"trace: OK — {len(covers)} ID có spec covers, {len(test_ids)} ID có test, {len(statuses)} ADR, cảnh báo: {len(warns)}")


if __name__ == "__main__":
    main()
