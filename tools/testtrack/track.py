#!/usr/bin/env python3
"""
track.py — RobotOps test tracker.
Nguồn sự thật: docs/test-status.json. Render: docs/test-status.md.
KHÔNG sửa tay 2 file đó — mọi thay đổi đi qua script này kèm evidence.

Cách dùng:
  go test -json ./... | python3 tools/testtrack/track.py --go-json -
  python3 tools/testtrack/track.py --go-json out.jsonl
  python3 tools/testtrack/track.py --hw OTA-04 --result pass --evidence docs/evidence/hw/OTA-04_2026-07-09.md
  python3 tools/testtrack/track.py --render          # chỉ render lại md từ json
"""
import argparse, json, os, re, subprocess, sys
from datetime import datetime, timezone

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip() or "."
STATUS_JSON = os.path.join(ROOT, "docs", "test-status.json")
STATUS_MD = os.path.join(ROOT, "docs", "test-status.md")
EVIDENCE_DIR = os.path.join(ROOT, "docs", "evidence", "ci")

ID_RE = re.compile(r"(PRV|ACL|TEL|PRB|OTA|ALT|TRM|WLB|INS|LOD)-?(\d{2})(?!\d)")

# Catalog: ID -> (tier, mô tả ngắn). Đồng bộ với docs/05-test-catalog.md.
CATALOG = {
  # A. Provisioning
  "PRV-01": ("I", "Enroll token hợp lệ"), "PRV-02": ("I", "Token đã dùng/hết hạn"),
  "PRV-03": ("I", "Cert tự gia hạn <30 ngày"), "PRV-04": ("I", "Cert hết hạn hoàn toàn"),
  "PRV-05": ("H", "Enroll Jetson+Pi <5 phút"),
  # B. ACL
  "ACL-01": ("I", "Agent A publish topic B → từ chối"), "ACL-02": ("I", "Subscribe wildcard bị giới hạn"),
  "ACL-03": ("I", "Không cert → chặn tầng TLS"), "ACL-04": ("I", "Payload >64KB bị từ chối"),
  # C. Telemetry
  "TEL-01": ("U", "Test vectors validate đúng"), "TEL-02": ("I", "24h không leak, seq liền"),
  "TEL-03": ("I", "LWT khi rút mạng"), "TEL-04": ("I", "Replay đúng seq/ts sau reconnect"),
  "TEL-05": ("I", "Buffer 24h+ downsample"), "TEL-06": ("I", "Clock skew >30s có event"),
  "TEL-07": ("H", "Field lạ không gây lỗi"),
  # D. Probe API
  "PRB-01": ("U", "apiVersion sai → từ chối sạch"), "PRB-02": ("I", "AMR profile lên dashboard"),
  "PRB-03": ("I", "Probe chết → degraded, agent sống"), "PRB-04": ("I", "Probe restart không nhân đôi"),
  "PRB-05": ("I", "2 probe Mode B hợp nhất inventory"), "PRB-06": ("H", "Kill node ROS thật → alarm ≤10s"),
  # E. OTA
  "OTA-01": ("I", "Deploy pass toàn state machine"), "OTA-02": ("I", "Health fail → tự rollback"),
  "OTA-03": ("I", "Crash-loop → tự rollback"), "OTA-04": ("H", "Rút điện giữa DOWNLOADING"),
  "OTA-05": ("H", "Rút điện giữa SWITCHING"), "OTA-06": ("I", "Rút mạng giữa download"),
  "OTA-07": ("I", "Digest sai → không start"), "OTA-08": ("I", "Lệnh quá hạn → rejected"),
  "OTA-09": ("I", "Staged rollout dừng khi wave fail"), "OTA-10": ("I", "Deploy chồng → từ chối"),
  "OTA-11": ("H", "Disk đầy → fail sạch"), "OTA-12": ("H", "Ma trận Jetson+Pi đủ OTA-01→05"),
  # F. Alert
  "ALT-01": ("I", "Offline → notify ≤60s"), "ALT-02": ("I", "Raised/cleared không spam"),
  "ALT-03": ("I", "50 robot offline → gộp tin"), "ALT-04": ("I", "Webhook chết → retry giới hạn"),
  # G. Terminal
  "TRM-01": ("I", "PTY + audit log đầy đủ"), "TRM-02": ("I", "Viewer bị chặn terminal"),
  "TRM-03": ("I", "Rớt mạng → phiên đóng sạch"), "TRM-04": ("I", "Log tail tự tắt theo TTL"),
  # H. White-label & Installer
  "WLB-01": ("I", "Theming không cần rebuild"), "INS-01": ("H", "Người ngoài cài <30 phút"),
  "INS-02": ("I", "install.sh idempotent"), "INS-03": ("I", "Backup/restore Postgres"),
  # I. Load
  "LOD-01": ("I", "50 agent 72h không mất QoS1"), "LOD-02": ("I", "Bão reconnect có backpressure"),
  "LOD-03": ("H", "30 ngày fleet thật, 0 brick"),
}

GROUPS = [("A · Provisioning", "PRV"), ("B · ACL cách ly", "ACL"), ("C · Telemetry/offline", "TEL"),
          ("D · Probe API", "PRB"), ("E · OTA ⭐", "OTA"), ("F · Alert", "ALT"),
          ("G · Terminal/log", "TRM"), ("H · White-label/Installer", ("WLB", "INS")),
          ("I · Tải & bền bỉ", "LOD")]

ICON = {"pending": "⬜", "pass": "✅", "fail": "❌", "stale": "⚠️"}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_commit():
    r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or "nogit"


def load():
    if os.path.exists(STATUS_JSON):
        with open(STATUS_JSON) as f:
            return json.load(f)
    return {"updated": None, "commit": None,
            "tests": {tid: {"status": "pending", "tier": tier, "desc": desc,
                             "lastRun": None, "commit": None, "evidence": None, "runs": 0}
                      for tid, (tier, desc) in CATALOG.items()}}


def save(state):
    os.makedirs(os.path.dirname(STATUS_JSON), exist_ok=True)
    state["updated"], state["commit"] = now(), git_commit()
    with open(STATUS_JSON, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    render(state)


def norm_id(name):
    m = ID_RE.search(name)
    return f"{m.group(1)}-{m.group(2)}" if m else None


def ingest_go_json(state, stream):
    """Parse `go test -json`. Một test Go có thể cover nhiều ID (ghi trong tên hoặc subtests)."""
    ts = now()
    ev_dir = os.path.join(EVIDENCE_DIR, f"{ts.replace(':', '')}-{git_commit()}")
    os.makedirs(ev_dir, exist_ok=True)
    raw_path = os.path.join(ev_dir, "raw.jsonl")
    results = {}
    with open(raw_path, "w") as raw:
        for line in stream:
            raw.write(line if line.endswith("\n") else line + "\n")
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("Action") not in ("pass", "fail") or "Test" not in ev:
                continue
            tid = norm_id(ev["Test"])
            if tid and tid in CATALOG:
                # fail thắng pass nếu nhiều subtest cùng ID
                results[tid] = "fail" if results.get(tid) == "fail" else ev["Action"]
    rel = os.path.relpath(raw_path, ROOT)
    changed = []
    for tid, res in results.items():
        t = state["tests"][tid]
        t.update(status=res, lastRun=now(), commit=git_commit(), evidence=rel,
                 runs=t["runs"] + 1)
        changed.append((tid, res))
    return changed


def set_hw(state, tid, result, evidence):
    if tid not in CATALOG:
        sys.exit(f"ID không có trong catalog: {tid}")
    if CATALOG[tid][0] != "H":
        sys.exit(f"{tid} không phải test [H] — dùng đường go-json")
    if not os.path.exists(os.path.join(ROOT, evidence)):
        sys.exit(f"Không tick khi thiếu file evidence: {evidence}")
    t = state["tests"][tid]
    t.update(status=result, lastRun=now(), commit=git_commit(),
             evidence=evidence, runs=t["runs"] + 1)
    return [(tid, result)]


def render(state):
    tests = state["tests"]
    total = len(tests)
    done = sum(1 for t in tests.values() if t["status"] == "pass")
    lines = [
        "# RobotOps — Test Status",
        "",
        f"> ⚙️ File này do `tools/testtrack/track.py` sinh — **không sửa tay**.",
        f"> Cập nhật: {state['updated']} · commit `{state['commit']}` · "
        f"**{done}/{total} ✅** ({100 * done // total}%)",
        "",
    ]
    for gname, prefix in GROUPS:
        prefixes = prefix if isinstance(prefix, tuple) else (prefix,)
        ids = [i for i in CATALOG if i.split("-")[0] in prefixes]
        gdone = sum(1 for i in ids if tests[i]["status"] == "pass")
        bar = "█" * gdone + "░" * (len(ids) - gdone)
        lines += [f"## {gname} — {gdone}/{len(ids)} `{bar}`", "",
                  "| | ID | Tầng | Mô tả | Lần cuối | Evidence |",
                  "|---|---|---|---|---|---|"]
        for i in ids:
            t = tests[i]
            ev = f"[log]({t['evidence']})" if t["evidence"] else "—"
            last = f"{t['lastRun'][:10]} `{t['commit']}`" if t["lastRun"] else "—"
            lines.append(f"| {ICON[t['status']]} | {i} | [{t['tier']}] | {t['desc']} | {last} | {ev} |")
        lines.append("")
    with open(STATUS_MD, "w") as f:
        f.write("\n".join(lines))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--go-json", help="file jsonl từ `go test -json`, hoặc - cho stdin")
    p.add_argument("--hw", help="ID test phần cứng, ví dụ OTA-04")
    p.add_argument("--result", choices=["pass", "fail"])
    p.add_argument("--evidence", help="đường dẫn biên bản evidence (bắt buộc với --hw)")
    p.add_argument("--render", action="store_true", help="chỉ render lại md")
    a = p.parse_args()

    state = load()
    changed = []
    if a.go_json:
        stream = sys.stdin if a.go_json == "-" else open(a.go_json)
        changed = ingest_go_json(state, stream)
    elif a.hw:
        if not (a.result and a.evidence):
            sys.exit("--hw cần cả --result và --evidence")
        changed = set_hw(state, a.hw, a.result, a.evidence)
    save(state)
    for tid, res in changed:
        print(f"{ICON[res]} {tid} → {res}")
    if not changed and not a.render:
        print("Không có ID nào khớp trong output — kiểm tra naming TestXXX##_...")


if __name__ == "__main__":
    main()
