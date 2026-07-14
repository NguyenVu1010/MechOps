#!/usr/bin/env python3
"""
hwtest.py — Biên bản test phần cứng [H] có evidence.
  python3 tools/testtrack/hwtest.py OTA-04 --tester Ng
Hỏi từng bước checklist → sinh docs/evidence/hw/<ID>_<date>.md → gọi track.py tick.
"""
import argparse, os, subprocess, sys
from datetime import date

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip() or "."

# Checklist từng ID [H] — đồng bộ với docs/05-test-catalog.md
CHECKLISTS = {
    "PRV-05": ["Cài bằng script curl|sh trên Jetson", "Cài bằng script trên Pi",
               "Cả hai enroll xong < 5 phút", "Xuất hiện trên dashboard"],
    "TEL-07": ["Publish payload có field lạ (mô phỏng version mới)",
               "Agent không lỗi/crash", "Server ghi nhận bình thường"],
    "PRB-06": ["Kill node nav2 trên robot thật", "Event ROS_NODE_DOWN ≤ 10s",
               "Alarm hiện trên dashboard"],
    "OTA-04": ["Bắt đầu deploy, xác nhận state=DOWNLOADING", "RÚT ĐIỆN vật lý",
               "Cấp điện lại, chờ boot", "App CŨ chạy bình thường",
               "Dashboard hiện deploy fail có lý do", "Không mất dữ liệu buffer"],
    "OTA-05": ["Bắt đầu deploy, chờ đúng state=SWITCHING", "RÚT ĐIỆN vật lý",
               "Cấp điện lại, chờ boot", "Agent tự rollback về version cũ",
               "Không tồn tại trạng thái 'không app nào chạy'"],
    "OTA-11": ["Làm đầy disk còn < kích thước image", "Deploy → fail sạch ở DOWNLOADING",
               "Lỗi rõ ràng trên dashboard", "App đang chạy không bị ảnh hưởng"],
    "OTA-12": ["OTA-01→05 pass trên Jetson (đính kèm ID biên bản)",
               "OTA-01→05 pass trên Pi (đính kèm ID biên bản)"],
    "INS-01": ["Người NGOÀI team, VPS trống, chỉ có docs", "Cài xong < 30 phút",
               "Không phải hỏi ai câu nào", "Ghi lại các chỗ vấp vào phần ghi chú"],
    "LOD-03": ["Fleet design partner ≥ 5 robot, 30 ngày", "0 sự cố brick",
               "Uptime agent ≥ 99.5% (đính kèm số liệu)"],
}


def ask(q):
    while True:
        r = input(f"  [{q}]  pass/fail/skip? ").strip().lower()
        if r in ("pass", "fail", "skip", "p", "f", "s"):
            return {"p": "pass", "f": "fail", "s": "skip"}.get(r, r)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("id")
    p.add_argument("--tester", required=True)
    p.add_argument("--hardware", default="", help="ví dụ: Jetson Orin Nano / Pi 4")
    a = p.parse_args()
    tid = a.id.upper()
    if tid not in CHECKLISTS:
        sys.exit(f"{tid} không có checklist [H]. Có: {', '.join(CHECKLISTS)}")

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    print(f"\n=== Biên bản {tid} · tester: {a.tester} · commit: {commit} ===\n")
    steps, overall = [], "pass"
    for step in CHECKLISTS[tid]:
        r = ask(step)
        if r == "fail":
            overall = "fail"
        steps.append((step, r))
    notes = input("\nGhi chú (enter nếu không): ").strip()

    ev_rel = f"docs/evidence/hw/{tid}_{date.today().isoformat()}.md"
    ev_abs = os.path.join(ROOT, ev_rel)
    os.makedirs(os.path.dirname(ev_abs), exist_ok=True)
    icon = {"pass": "✅", "fail": "❌", "skip": "⏭"}
    with open(ev_abs, "w") as f:
        f.write(f"# Biên bản test phần cứng — {tid}\n\n")
        f.write(f"- Ngày: {date.today().isoformat()}\n- Tester: {a.tester}\n")
        f.write(f"- Phần cứng: {a.hardware or 'chưa ghi'}\n- Commit: `{commit}`\n")
        f.write(f"- Kết quả: **{overall.upper()}**\n\n## Các bước\n\n")
        for s, r in steps:
            f.write(f"- {icon[r]} {s}\n")
        if notes:
            f.write(f"\n## Ghi chú\n\n{notes}\n")
    print(f"\nĐã ghi biên bản: {ev_rel}")

    subprocess.run([sys.executable, os.path.join(ROOT, "tools/testtrack/track.py"),
                    "--hw", tid, "--result", overall, "--evidence", ev_rel], check=True)


if __name__ == "__main__":
    main()
