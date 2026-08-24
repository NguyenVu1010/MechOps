#!/usr/bin/env python3
"""steer.py — nhật ký hành động có truy vết (.steering/).

Bốn hệ hồ sơ đang có đều chỉ ghi thứ SỐNG SÓT:
    git                — mã còn lại sau khi đã vứt bỏ
    docs/evidence/     — kết quả test đã chạy
    docs/adr/          — quyết định đã chốt
    docs/test-status.* — trạng thái hiện tại

Không hệ nào ghi được thứ đắt nhất khi truy vết sáu tháng sau: **cái đã thử và
bỏ**, và **vì sao bỏ**. Không có nó, người sau (hoặc chính agent ở phiên khác)
sẽ thử lại đúng con đường đã hỏng.

Mục nhật ký bất biến như ADR: viết rồi không sửa. Sai thì viết mục mới với
`supersedes: [S000N]`.

    steer.py new --kind attempt --area agent --ids OTA-07 --title "..." --why "..."
    steer.py close --last --outcome reverted --why "..." --promoted "OTA-13"
    steer.py index · list · show S0007
"""
import argparse
import datetime as dt
import os
import re
import subprocess
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STEER_DIR = os.path.join(ROOT, ".steering")
ENTRIES = os.path.join(STEER_DIR, "entries")
PLANS = os.path.join(STEER_DIR, "plans")
INDEX = os.path.join(STEER_DIR, "INDEX.md")
STATUS_MD = os.path.join(ROOT, "docs", "test-status.md")

sys.path.insert(0, os.path.join(ROOT, "tools", "testtrack"))
try:
    from track import CATALOG
except Exception:                              # tracker hỏng không được chặn ghi nhật ký
    CATALOG = {}

# Năm loại. Cố ý ít: `revert` không phải loại riêng (là attempt + outcome reverted),
# `fix` cũng không (bug của chính mình thì nhà của nó là một test ID mới).
KINDS = {
    "attempt":   "thử một hướng đi chưa chắc",
    "wrong":     "giả định đã tin là đúng, hoá ra sai",
    "discovery": "phát hiện về hệ thống, chưa thành bug",
    "decision":  "quyết định nhỏ, chưa tới mức ADR",
    "risky":     "lệnh có sức phá hoại (hook tự ghi)",
}
# Trùng với đường ranh module trong constitution #7 + go-conventions, để lọc được
# "mọi thứ từng thử ở tầng agent".
AREAS = ["agent", "server", "protocol", "probe", "dashboard", "specs", "infra", "flow"]
OUTCOMES = ["open", "kept", "reverted", "superseded"]

BODY_MAX = 30          # dòng thân tối đa; dài hơn thì nó là ADR hoặc test, không phải nhật ký
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
ID_RE = re.compile(r"^S(\d{4})-")


def sh(*a, default=""):
    try:
        r = subprocess.run(a, capture_output=True, text=True, cwd=ROOT, timeout=15)
        return r.stdout.strip() if r.returncode == 0 else default
    except Exception:
        return default


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slug(s, n=42):
    """Tên file chỉ ASCII — repo đi qua Windows, container Linux và CI."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "D")
    s = re.sub(r"[^A-Za-z0-9\s-]", "", s).strip().lower()
    return re.sub(r"[\s_]+", "-", s)[:n].strip("-") or "khong-ten"


def q(s):
    """Giá trị an toàn cho frontmatter — dấu ':' giữa scalar không trích dẫn làm vỡ YAML."""
    return '"' + str(s).replace("\\", "/").replace('"', "'").replace("\n", " ").strip() + '"'


def parse_fm(path):
    """Frontmatter thô. Không dùng yaml: truy vết mà vỡ vì một mục viết hỏng thì vô dụng."""
    m = FM_RE.match(open(path, encoding="utf-8").read())
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm


def paths():
    if not os.path.isdir(ENTRIES):
        return []
    return sorted(os.path.join(ENTRIES, n) for n in os.listdir(ENTRIES) if ID_RE.match(n))


def next_id():
    used = [int(ID_RE.match(os.path.basename(p)).group(1)) for p in paths()]
    return f"S{max(used) + 1 if used else 1:04d}"


def open_milestone():
    if os.path.exists(STATUS_MD):
        for line in open(STATUS_MD, encoding="utf-8"):
            m = re.search(r"Milestone đang mở: (M\d)", line)
            if m:
                return m.group(1)
    return "?"


def latest_evidence():
    d = os.path.join(ROOT, "docs", "evidence", "ci")
    if not os.path.isdir(d):
        return ""
    dirs = sorted(os.listdir(d))
    return f"docs/evidence/ci/{dirs[-1]}" if dirs else ""


# ------------------------------------------------------------------ new

TEMPLATE = """
## Vì sao đụng tới
{context}

## Tin rằng
{belief}

## Đã làm
{did}

## Bằng chứng
{proof}

## Kết luận
<điền khi đóng>

## Đã nâng thành
<điền khi đóng: test ID / ADR-00NN / dòng trong skill nào / none>
"""

RISKY_TEMPLATE = """
## Vì sao đụng tới
{context}

## Lệnh
```
{command}
```

## Kết luận
<điền khi đóng>

## Đã nâng thành
<điền khi đóng: test ID / ADR-00NN / dòng trong skill nào / none>
"""


def plan_names():
    if not os.path.isdir(PLANS):
        return []
    return sorted(n for n in os.listdir(PLANS)
                  if os.path.isdir(os.path.join(PLANS, n)))


def plan_fm(name):
    """Frontmatter của spec.md — nơi khai covers/adr/status của cả plan."""
    p = os.path.join(PLANS, name, "spec.md")
    return parse_fm(p) if os.path.exists(p) else {}


def bullets(s, placeholder):
    """Nhiều mục phân tách bằng ' | ' -> gạch đầu dòng."""
    if not s:
        return placeholder
    return "\n".join(f"- {x.strip()}" for x in s.split("|") if x.strip())


def cmd_new(a):
    if a.kind not in KINDS:
        sys.exit(f"kind không hợp lệ. Chọn: {', '.join(KINDS)}")
    if a.area not in AREAS:
        sys.exit(f"area không hợp lệ. Chọn: {', '.join(AREAS)}")

    ids = [i.strip().upper() for i in (a.ids or "").split(",") if i.strip()]
    if CATALOG:
        for i in ids:
            if i not in CATALOG:
                sys.exit(f"test ID {i} không có trong catalog — thêm ID trước "
                         "(skill bug-to-test), rồi mới ghi nhật ký.")
    sup = [s.strip().upper() for s in (a.supersedes or "").split(",") if s.strip()]
    have = {parse_fm(p).get("id") for p in paths()}
    for s in sup:
        if s not in have:
            sys.exit(f"supersedes trỏ tới mục không tồn tại: {s}")

    plan = a.plan or ""
    if plan and plan not in plan_names():
        sys.exit(f"plan {plan!r} không có trong .steering/plans/. "
                 f"Có: {', '.join(plan_names()) or '(chưa có plan nào)'}")

    sid = next_id()
    os.makedirs(ENTRIES, exist_ok=True)
    path = os.path.join(ENTRIES, f"{sid}-{a.kind}-{slug(a.title)}.md")

    fm = [
        "---",
        f"id: {sid}",
        f"date: {now()}",
        f"kind: {a.kind}",
        f"outcome: {a.outcome}",
        f"title: {q(a.title)}",
        f"area: {a.area}",
        f"plan: {plan}",
        f"milestone: {plan_fm(plan).get('milestone') if plan else open_milestone()}",
        f"test_ids: [{', '.join(ids)}]",
        f"supersedes: [{', '.join(sup)}]",
        f"branch: {q(sh('git', 'rev-parse', '--abbrev-ref', 'HEAD', default='?'))}",
        f"commit: {sh('git', 'rev-parse', '--short', 'HEAD', default='?')}",
        f"evidence: {q(latest_evidence())}",
        f"promoted_to: {q('')}",
        f"source: {a.source}",
        "---",
        "",
        f"# {sid} · {a.title}",
        "",
    ]
    if a.kind == "risky":
        body = RISKY_TEMPLATE.format(
            context=a.context or "<điền: đang làm gì mà cần lệnh này>",
            command=a.command or "",
        )
    else:
        body = TEMPLATE.format(
            context=a.context or "<điền: cái gì dẫn tới hành động này>",
            belief=a.why or "<điền ở thì tin-là-đúng: 'tưởng rằng ...'>",
            did=bullets(a.did, "- <file / lệnh cụ thể>"),
            proof=a.proof or "<quan sát đã kết luận: file:dòng, output lệnh, dòng log "
                             "— không phải cảm nhận>",
        )
    open(path, "w", encoding="utf-8").write("\n".join(fm) + body)
    rebuild_index()
    print(f"{sid}  {os.path.relpath(path, ROOT)}")


# ------------------------------------------------------------------ close

def cmd_close(a):
    ps = paths()
    if not ps:
        sys.exit("chưa có mục nào trong .steering/entries/")

    if a.last:
        # "mục cuối" = mục ĐANG MỞ mới nhất, không phải file mới nhất. Hook có thể
        # chèn một mục `risky` vào giữa lúc agent đang làm dở; bám theo file mới
        # nhất thì agent đóng nhầm mục của hook và cả hai bản ghi cùng sai.
        opened = [p for p in ps if parse_fm(p).get("outcome") == "open"]
        if not opened:
            sys.exit("không có mục nào đang mở. Xem `steer.py list`, đóng theo id.")
        path = opened[-1]
    else:
        hit = [p for p in ps if a.entry and a.entry.upper() in os.path.basename(p).upper()]
        if len(hit) != 1:
            sys.exit(f"không xác định được mục từ {a.entry!r} ({len(hit)} khớp)")
        path = hit[0]

    fm = parse_fm(path)
    if fm.get("outcome") != "open":
        sys.exit(f"{fm.get('id')} đã đóng ({fm.get('outcome')}). Mục bất biến — "
                 f"viết mục mới với --supersedes {fm.get('id')}.")

    text = open(path, encoding="utf-8").read()
    text = re.sub(r"^outcome: .*$", f"outcome: {a.outcome}", text, count=1, flags=re.M)
    text = re.sub(r"^promoted_to: .*$", f"promoted_to: {q(a.promoted)}", text, count=1, flags=re.M)
    text = text.replace(
        "## Kết luận\n<điền khi đóng>",
        f"## Kết luận\n**{a.outcome}** — {a.why}\n\n"
        f"_Đóng {now()} · commit `{sh('git', 'rev-parse', '--short', 'HEAD', default='?')}`_",
    )
    text = re.sub(r"## Đã nâng thành\n<điền khi đóng[^>]*>",
                  f"## Đã nâng thành\n{a.promoted}", text)
    open(path, "w", encoding="utf-8").write(text)
    rebuild_index()
    print(f"{fm.get('id')}  {a.outcome}  → {a.promoted}")


# ------------------------------------------------------------------ index

def rebuild_index():
    rows = []
    for p in paths():
        fm = parse_fm(p)
        rows.append({**fm, "file": os.path.basename(p)})
    rows.sort(key=lambda r: r.get("id", ""), reverse=True)

    n_open = sum(1 for r in rows if r.get("outcome") == "open")
    kinds = {}
    for r in rows:
        kinds[r.get("kind", "?")] = kinds.get(r.get("kind", "?"), 0) + 1

    L = ["# .steering — mục lục", "",
         "> ⚙️ Sinh bởi `tools/steering/steer.py` — **không sửa tay**. "
         "Luật và format: `.steering/README.md`.",
         f"> {len(plan_names())} plan · {len(rows)} mục nhật ký · {n_open} chưa đóng · "
         + " · ".join(f"{k} {v}" for k, v in sorted(kinds.items())), ""]

    # Plan trước nhật ký: người mở file này thường đi tìm "feature X đang tới đâu",
    # không phải "mục S0007 là gì".
    if plan_names():
        L += ["## Plan", "",
              "| Plan | Milestone | Trạng thái | Covers | ADR | Nhật ký |",
              "|---|---|---|---|---|---|"]
        for name in plan_names():
            pf = plan_fm(name)
            n_j = sum(1 for r in rows if r.get("plan") == name)
            L.append(f"| [{name}](plans/{name}/) | {pf.get('milestone', '—')} "
                     f"| {gate_summary(name)} | {pf.get('covers', '[]').strip('[]') or '—'} "
                     f"| {pf.get('adr', '[]').strip('[]') or '—'} "
                     f"| [{n_j} mục](plans/{name}/JOURNAL.md) |")
        L.append("")

    if n_open:
        L += ["## ⚠️ Chưa đóng — nợ chưa trả", "",
              "| id | Loại | Tầng | Tiêu đề |", "|---|---|---|---|"]
        for r in rows:
            if r.get("outcome") == "open":
                L.append(f"| [{r.get('id')}](entries/{r['file']}) | {r.get('kind')} "
                         f"| {r.get('area')} | {r.get('title')} |")
        L.append("")

    # Gom theo milestone: repo tổ chức mọi thứ theo milestone, nhật ký cũng vậy —
    # đóng milestone thì đọc lại đúng phần của nó.
    by_ms = {}
    for r in rows:
        by_ms.setdefault(r.get("milestone", "?"), []).append(r)

    for ms in sorted(by_ms, reverse=True):
        L += [f"## {ms}", "",
              "| id | Ngày | Loại | Kết cục | Tầng | Test ID | Đã nâng thành | Tiêu đề |",
              "|---|---|---|---|---|---|---|---|"]
        for r in by_ms[ms]:
            L.append(
                f"| [{r.get('id')}](entries/{r['file']}) | {r.get('date', '')[:10]} "
                f"| {r.get('kind')} | {r.get('outcome')} | {r.get('area')} "
                f"| {r.get('test_ids', '[]').strip('[]') or '—'} "
                f"| {r.get('promoted_to') or '—'} | {r.get('title')} |")
        L.append("")

    os.makedirs(STEER_DIR, exist_ok=True)
    open(INDEX, "w", encoding="utf-8").write("\n".join(L))
    rebuild_journals()
    for n in plan_names():
        rebuild_status(n)
    return len(rows)


def rebuild_journals():
    """JOURNAL.md của mỗi plan = mọi mục nhật ký gắn với plan đó.

    Đây là chỗ 'plan' và 'implement' gặp nhau: mở thư mục plan ra là thấy cả thứ
    đã định làm lẫn thứ đã thử rồi bỏ, không phải nhảy sang thư mục khác.
    """
    rows_by_plan = {}
    for p in paths():
        fm = parse_fm(p)
        if fm.get("plan"):
            rows_by_plan.setdefault(fm["plan"], []).append((fm, os.path.basename(p)))

    for name in plan_names():
        rows = sorted(rows_by_plan.get(name, []), key=lambda r: r[0].get("id", ""), reverse=True)
        L = [f"# {name} — nhật ký hành động", "",
             "> ⚙️ Sinh bởi `tools/steering/steer.py` — **không sửa tay**. "
             "Mục nhật ký nằm ở `../../entries/`.",
             f"> {len(rows)} mục · {sum(1 for r, _ in rows if r.get('outcome') == 'open')} chưa đóng", ""]
        if not rows:
            L += ["Chưa có mục nào. Gắn mục vào plan này bằng:", "",
                  f"```\n./mo steer new --kind attempt --plan {name} --area agent \\\n"
                  "    --title \"...\" --why \"...\"\n```", ""]
        else:
            L += ["| id | Loại | Kết cục | Test ID | Đã nâng thành | Tiêu đề |",
                  "|---|---|---|---|---|---|"]
            for fm, f in rows:
                L.append(f"| [{fm.get('id')}](../../entries/{f}) | {fm.get('kind')} "
                         f"| {fm.get('outcome')} | {fm.get('test_ids', '[]').strip('[]') or '—'} "
                         f"| {fm.get('promoted_to') or '—'} | {fm.get('title')} |")
            L.append("")
        open(os.path.join(PLANS, name, "JOURNAL.md"), "w", encoding="utf-8").write("\n".join(L))
    return len(plan_names())


def cmd_index(a):
    n = rebuild_index()
    m = rebuild_journals()
    print(f"steering: {n} mục · {m} plan · .steering/INDEX.md + JOURNAL.md từng plan")


# ------------------------------------------------------------------ list / show

def cmd_list(a):
    n = 0
    for p in paths():
        fm = parse_fm(p)
        if a.kind and fm.get("kind") != a.kind:
            continue
        if a.area and fm.get("area") != a.area:
            continue
        if a.id and a.id.upper() not in fm.get("test_ids", ""):
            continue
        if a.plan and fm.get("plan") != a.plan:
            continue
        if a.open and fm.get("outcome") != "open":
            continue
        print(f"{fm.get('id')}  {fm.get('date', '')[:10]}  {fm.get('kind', ''):9} "
              f"{fm.get('outcome', ''):10} {fm.get('area', ''):9} "
              f"{(fm.get('plan') or '—'):14} {fm.get('title', '')}")
        n += 1
    if not n:
        print("(không có mục nào khớp)")


# ------------------------------------------------------------------ plan

PLAN_FILES = {
    "spec.md": ("CÁI GÌ", [
        "## Hành vi mong đợi", "<viết bằng thứ quan sát được từ bên ngoài>", "",
        "## Ngoài scope", "<thứ cố tình KHÔNG làm, để người review khỏi đi tìm>", "",
        "## Nguồn yêu cầu", "<mục nào trong docs/product/ hoặc ADR nào dẫn tới feature này>",
    ]),
    "clarify.md": ("CHƯA RÕ CÁI GÌ", [
        "> Agent điền câu hỏi. **Người** điền đáp án. Chưa có đáp án thì chưa sang plan.md.", "",
        "### 1. <câu hỏi>", "**Đáp:**", "",
    ]),
    "plan.md": ("LÀM THẾ NÀO", [
        "## 1. Delta hợp đồng `specs/`", "<field/topic/message nào đổi; field mới phải optional>", "",
        "## 2. State machine", "<state → sự kiện → state; ghi SQLite lúc nào>", "",
        "## 3. Ma trận thất bại", "",
        "| Hỏng ở đâu | Lúc nào | Hành vi mong đợi | Test ID |", "|---|---|---|---|",
        "| mất điện |  |  |  |", "| mất mạng |  |  |  |",
        "| disk đầy |  |  |  |", "| lệch giờ |  |  |  |", "",
        "## 4. Chia tầng test", "<ID nào [U] / [I] / [H]>", "",
        "## 5. Đường ranh module", "<code mới nằm đâu, vì sao không nằm chỗ khác>", "",
        "## 6. Quyết định cần ADR", "<liệt kê, hoặc ghi rõ 'không có'>",
    ]),
    "testcases.md": ("LÀM SAO BIẾT XONG", [
        "> Đây là **thiết kế test**, không phải danh sách ID. Danh sách ID là",
        "> `docs/product/05-test-catalog.md` — nguồn sự thật duy nhất, đừng chép lại.",
        "> Mỗi mục dưới đây là một ID trong `covers:` của spec.md.", "",
        "## <TEST-ID> · [tầng] · <mô tả ngắn từ catalog>", "",
        "- **Tiền đề:** <trạng thái ban đầu, fixture, dữ liệu cần có>",
        "- **Thao tác:** <làm gì để kích hoạt>",
        "- **Mong đợi:** <quan sát được từ bên ngoài, không phải 'không lỗi'>",
        "- **Bằng chứng:** <dòng log nào, hàng nào trong DB, event nào>",
        "- **Tên test:** `Test<ID bỏ gạch>_<MôTả>`", "",
        "## ID đề xuất thêm vào catalog", "",
        "> Hành vi feature này cần canh mà catalog chưa có ID. Thêm vào",
        "> `05-test-catalog.md` + `CATALOG` của `track.py` CÙNG một commit",
        "> (quy tắc catalog #3) TRƯỚC khi dùng — `./mo trace` sẽ chặn nếu quên.", "",
        "- <chưa có / hoặc: OTA-13 — [I] — mô tả hành vi>",
    ]),
    "tasks.md": ("THỨ TỰ", [
        "> Task ≤ nửa ngày, mỗi task ≥1 test ID. Task không có ID = task không hợp lệ.",
        "> **Dấu tích do máy điền** (`./mo steer plan sync`): task xanh khi MỌI test ID",
        "> của nó đã pass trong tracker. Tick tay sẽ bị `./mo trace` chặn — đó là",
        "> cách tasks.md biến thành nguồn 'đã xong' thứ hai và nói dối.", "",
        "- [ ] T1 — <mô tả> · `<TEST-ID>`",
    ]),
}

# Thứ tự chốt. Mỗi artifact chỉ chốt được khi cái trước đã chốt — gate tuần tự,
# vì bẻ task từ một plan chưa chốt là bẻ theo thứ có thể đổi dưới chân mình.
LOCK_ORDER = ["spec", "plan", "testcases", "tasks"]
LOCK_FILE = {k: f"{k}.md" for k in LOCK_ORDER}


PLACEHOLDER = re.compile(r"<(điền|viết|liệt kê|mô tả|state|quan sát|file|câu hỏi|ID|TEST-ID|tầng|chưa có|thứ|field|code)")
TASK_RE = re.compile(r"^(\s*-\s*)\[([ xX])\](\s+.*)$")
# TID_RE = test ID. KHÔNG đặt tên ID_RE: hằng đó đã dùng cho id mục nhật ký
# (^S\d{4}-) ở paths()/next_id(); trùng tên làm paths() trả rỗng và next_id() cấp trùng.
TID_RE = re.compile(r"[A-Z]{3}-\d{2}")


def _set_status(path, value):
    t = open(path, encoding="utf-8").read()
    open(path, "w", encoding="utf-8").write(
        re.sub(r"^status: .*$", f"status: {value}", t, count=1, flags=re.M))


def _body(path):
    if not os.path.exists(path):
        return ""
    return open(path, encoding="utf-8").read().split("\n---\n", 1)[-1]


def file_status(name, fn):
    return parse_fm(os.path.join(PLANS, name, fn)).get("status", "?")


def tracker_pass():
    """{ID: True/False} — ID nào đang xanh trong tracker."""
    p = os.path.join(ROOT, "docs", "test-status.json")
    if not os.path.exists(p):
        return {}
    import json
    tests = json.load(open(p, encoding="utf-8"))["tests"]
    return {k: v.get("status") == "pass" for k, v in tests.items()}


def sync_tasks(name):
    """Tick lại tasks.md TỪ TRACKER. Không bao giờ tin dấu tích có sẵn.

    Task xanh khi MỌI test ID của nó đã pass. Đây là chỗ constitution #2
    ("tick chỉ do máy") áp cho tasks.md — để nó không thành nguồn 'đã xong'
    thứ hai mâu thuẫn với test-status.md.
    """
    p = os.path.join(PLANS, name, "tasks.md")
    if not os.path.exists(p):
        return 0, 0
    passing = tracker_pass()
    out, done, total = [], 0, 0
    for line in open(p, encoding="utf-8").read().splitlines():
        m = TASK_RE.match(line)
        if not m:
            out.append(line)
            continue
        ids = TID_RE.findall(m.group(3))
        total += 1
        ok = bool(ids) and all(passing.get(i) for i in ids)
        done += ok
        out.append(f"{m.group(1)}[{'x' if ok else ' '}]{m.group(3)}")
    open(p, "w", encoding="utf-8").write("\n".join(out) + "\n")
    return done, total


def rebuild_status(name):
    """STATUS.md — mặt tiền của feature. Máy sinh, mở ra là biết đang ở đâu."""
    d = os.path.join(PLANS, name)
    fm = plan_fm(name)
    covers = TID_RE.findall(fm.get("covers", ""))
    passing = tracker_pass()
    t_done, t_total = sync_tasks(name)
    n_j = sum(1 for p in paths() if parse_fm(p).get("plan") == name)
    n_open = sum(1 for p in paths()
                 if parse_fm(p).get("plan") == name and parse_fm(p).get("outcome") == "open")

    def bar(a, b):
        return "" if not b else "█" * round(12 * a / b) + "░" * (12 - round(12 * a / b))

    c_done = sum(1 for i in covers if passing.get(i))
    icon = {"draft": "✏️", "locked": "🔒", "open": "❓", "answered": "✅"}

    L = [f"# {name} — trạng thái", "",
         "> ⚙️ Máy sinh (`./mo steer plan sync`) — **không sửa tay**.",
         f"> Milestone **{fm.get('milestone', '?')}** · "
         f"ADR {fm.get('adr', '[]')} · nguồn: xem `spec.md`", "",
         "## Cổng chốt", "",
         "| Artifact | Trạng thái | Nội dung |", "|---|---|---|"]
    for key, what in [("spec", "CÁI GÌ"), ("clarify", "CHƯA RÕ GÌ"), ("plan", "LÀM THẾ NÀO"),
                      ("testcases", "LÀM SAO BIẾT XONG"), ("tasks", "THỨ TỰ")]:
        st = file_status(name, f"{key}.md")
        L.append(f"| [{key}.md]({key}.md) | {icon.get(st, '·')} {st} | {what} |")

    L += ["", "## Tiến độ", "",
          f"- Task: **{t_done}/{t_total}** `{bar(t_done, t_total)}` — dấu tích do máy điền từ tracker",
          f"- Test ID: **{c_done}/{len(covers)}** `{bar(c_done, len(covers))}`", ""]
    if covers:
        L += ["| Test ID | Trạng thái |", "|---|---|"]
        for i in covers:
            L.append(f"| `{i}` | {'✅' if passing.get(i) else '⬜'} |")
        L.append("")
    L += [f"- Nhật ký: [{n_j} mục](JOURNAL.md)"
          + (f" · ⚠️ **{n_open} chưa đóng**" if n_open else ""), ""]
    open(os.path.join(d, "STATUS.md"), "w", encoding="utf-8").write("\n".join(L))


def gate_summary(name):
    """'2/4 chốt' — trạng thái của cả plan là số cổng đã qua, không phải status
    của riêng spec.md. Hiện status một file cho cả plan là nói dối về ba file kia."""
    st = [file_status(name, LOCK_FILE[k]) for k in LOCK_ORDER]
    if all(x == "frozen" for x in st):
        return "frozen"
    return f"{sum(1 for x in st if x in ('locked', 'frozen'))}/{len(LOCK_ORDER)} chốt"


def cmd_plan_sync(a):
    names = [a.name] if a.name else plan_names()
    for n in names:
        rebuild_status(n)
    rebuild_journals()
    print(f"steering: đồng bộ {len(names)} plan (tasks.md tick lại từ tracker, STATUS.md sinh lại)")


def cmd_plan_lock(a):
    if a.artifact not in LOCK_ORDER:
        sys.exit(f"artifact phải là một trong: {', '.join(LOCK_ORDER)}")
    d = os.path.join(PLANS, a.name)
    if not os.path.isdir(d):
        sys.exit(f"không có plan {a.name!r}")
    fn = LOCK_FILE[a.artifact]
    path = os.path.join(d, fn)

    if file_status(a.name, fn) == "locked":
        sys.exit(f"{a.artifact} đã chốt rồi. Đổi ý thì mở plan mới, hoặc `plan unlock` có lý do.")

    # Gate 1: cái trước phải chốt xong
    i = LOCK_ORDER.index(a.artifact)
    if i > 0:
        prev = LOCK_ORDER[i - 1]
        if file_status(a.name, LOCK_FILE[prev]) != "locked":
            sys.exit(f"chưa chốt {prev} thì chưa chốt được {a.artifact} — "
                     "gate tuần tự, bẻ task từ plan chưa chốt là bẻ theo thứ còn đổi được.")

    # Gate 2: clarify phải có đáp án trước khi chốt spec (đây là gate người)
    if a.artifact == "spec":
        cl = os.path.join(d, "clarify.md")
        body = _body(cl)
        if PLACEHOLDER.search(body) or "**Đáp:**\n\n" in body or body.rstrip().endswith("**Đáp:**"):
            sys.exit("clarify.md còn câu hỏi chưa có đáp án của founder — "
                     "constitution #9, agent không trả lời thay.")
        _set_status(cl, "answered")

    # Gate 3: nội dung không còn chỗ trống
    if PLACEHOLDER.search(_body(path)):
        sys.exit(f"{fn} còn chỗ chưa điền (<...>). Điền hết rồi chốt.")

    # Gate 4: tasks phải có ID thật và nằm trong covers
    if a.artifact == "tasks":
        covers = set(TID_RE.findall(plan_fm(a.name).get("covers", "")))
        bad = []
        for line in _body(path).splitlines():
            m = TASK_RE.match(line)
            if not m:
                continue
            ids = TID_RE.findall(m.group(3))
            if not ids:
                bad.append(f"task không có test ID: {line.strip()[:60]}")
            elif set(ids) - covers:
                bad.append(f"ID ngoài covers: {', '.join(sorted(set(ids) - covers))}")
        if bad:
            sys.exit("\n".join(bad))

    # Gate 5: testcases phải có mục cho mọi ID trong covers
    if a.artifact == "testcases":
        covers = set(TID_RE.findall(plan_fm(a.name).get("covers", "")))
        have = set(TID_RE.findall(" ".join(
            l for l in _body(path).splitlines() if l.startswith("## "))))
        missing = sorted(covers - have)
        if missing:
            sys.exit(f"testcases.md thiếu thiết kế cho: {', '.join(missing)} — "
                     "mỗi ID trong covers phải có một mục `## <ID>`.")

    _set_status(path, "locked")
    rebuild_status(a.name)
    rebuild_index()
    nxt = LOCK_ORDER[i + 1] if i + 1 < len(LOCK_ORDER) else None
    print(f"{a.name}/{fn}: 🔒 locked"
          + (f" — tiếp theo chốt `{nxt}`" if nxt else " — cả bốn cổng đã chốt, vào /task được"))


def cmd_plan_new(a):
    name = slug(a.name, 48)
    d = os.path.join(PLANS, name)
    if os.path.isdir(d):
        sys.exit(f"plan {name!r} đã tồn tại")

    covers = [i.strip().upper() for i in (a.covers or "").split(",") if i.strip()]
    if CATALOG:
        for i in covers:
            if i not in CATALOG:
                sys.exit(f"covers trỏ ID không có trong catalog: {i}")
    if not covers:
        sys.exit("plan phải khai `--covers` với ≥1 test ID — feature không cover ID nào "
                 "là feature không hợp lệ (skill feature-spec).")
    adr = [x.strip() for x in (a.adr or "").split(",") if x.strip()]
    reqs = [x.strip() for x in (a.requirements or "").split(",") if x.strip()]

    os.makedirs(d)
    for fn, (what, body) in PLAN_FILES.items():
        # `status` là của TỪNG artifact, không phải của cả plan: spec chốt trước,
        # plan chốt sau, tasks chốt cuối. Chốt cả cụm một lần thì gate tuần tự
        # của SDD không tồn tại.
        st = "answered" if fn == "clarify.md" else "draft"
        fm = ["---", f"plan: {name}", f"milestone: {a.milestone}", f"status: {st}",
              f"covers: [{', '.join(covers)}]", f"adr: [{', '.join(adr)}]", "requirements:"]
        fm += [f"  - {r}" for r in reqs] or ["  - <điền nguồn yêu cầu>"]
        fm += ["---", "", f"# {name} · {fn.replace('.md', '')} — {what}", ""]
        open(os.path.join(d, fn), "w", encoding="utf-8").write("\n".join(fm + body) + "\n")
    # clarify chưa trả lời thì chưa phải "answered"
    _set_status(os.path.join(d, "clarify.md"), "open")

    rebuild_index()
    print(f"{name}  .steering/plans/{name}/")
    print("  spec · clarify · plan · testcases · tasks   (+ STATUS.md, JOURNAL.md máy sinh)")
    print("Bước tiếp: điền spec.md rồi clarify.md, DỪNG chờ founder trả lời.")


def cmd_plan_list(a):
    if not plan_names():
        print("(chưa có plan nào — ./mo steer plan new <ten> --milestone M3 --covers ...)")
        return
    for n in plan_names():
        pf = plan_fm(n)
        n_j = sum(1 for p in paths() if parse_fm(p).get("plan") == n)
        print(f"{n:24} {pf.get('milestone', '?'):4} {gate_summary(n):12} "
              f"covers={pf.get('covers', '[]')}  nhật ký={n_j}")


def cmd_plan_freeze(a):
    d = os.path.join(PLANS, a.name)
    if not os.path.isdir(d):
        sys.exit(f"không có plan {a.name!r}")
    # Chưa chốt cổng nào mà freeze thì khoá vĩnh viễn một bản nháp — mất cả
    # gate tuần tự lẫn khả năng sửa. Đây là đường một chiều, phải chặn.
    unlocked = [k for k in LOCK_ORDER if file_status(a.name, LOCK_FILE[k]) == "draft"]
    if unlocked and not a.force:
        sys.exit(f"chưa chốt: {', '.join(unlocked)}. Chốt hết bốn cổng rồi mới freeze "
                 "— freeze là một chiều, đóng băng bản nháp là mất luôn cả hai đường.")

    opened = [parse_fm(p).get("id") for p in paths()
              if parse_fm(p).get("plan") == a.name and parse_fm(p).get("outcome") == "open"]
    if opened and not a.force:
        sys.exit(f"còn mục nhật ký chưa đóng: {', '.join(opened)}. "
                 "Đóng trước, hoặc dùng --force nếu thật sự muốn đóng băng kèm nợ.")
    for fn in list(PLAN_FILES):
        p = os.path.join(d, fn)
        if os.path.exists(p):
            t = open(p, encoding="utf-8").read()
            open(p, "w", encoding="utf-8").write(
                re.sub(r"^status: .*$", "status: frozen", t, count=1, flags=re.M))
    rebuild_index()
    print(f"{a.name}: frozen — từ giờ bất biến, đổi ý thì mở plan mới")


def cmd_show(a):
    hit = [p for p in paths() if a.entry.upper() in os.path.basename(p).upper()]
    if len(hit) != 1:
        sys.exit(f"không xác định được mục từ {a.entry!r} ({len(hit)} khớp)")
    sys.stdout.write(open(hit[0], encoding="utf-8").read())


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="mở một mục")
    n.add_argument("--kind", required=True, help=" · ".join(f"{k}={v}" for k, v in KINDS.items()))
    n.add_argument("--title", required=True)
    n.add_argument("--area", default="flow", help=" | ".join(AREAS))
    n.add_argument("--ids", help="test ID liên quan, phân tách bằng dấu phẩy")
    n.add_argument("--context", help="cái gì dẫn tới hành động này")
    n.add_argument("--why", help="giả định, viết ở thì tin-là-đúng")
    n.add_argument("--did", help="đã làm gì; nhiều mục phân tách bằng ' | '")
    n.add_argument("--proof", help="bằng chứng quan sát được (file:dòng, output, log)")
    n.add_argument("--supersedes", help="id mục bị thay thế, ví dụ S0003")
    n.add_argument("--plan", help="gắn mục vào plan nào, ví dụ m3-ota-v1")
    n.add_argument("--outcome", default="open", choices=OUTCOMES)
    n.add_argument("--source", default="agent", choices=["agent", "hook", "human"])
    n.add_argument("--command", help="lệnh đã chạy (dùng với --kind risky)")
    n.set_defaults(func=cmd_new)

    c = sub.add_parser("close", help="đóng một mục bằng kết cục thật")
    c.add_argument("entry", nargs="?", help="id, ví dụ S0007")
    c.add_argument("--last", action="store_true", help="mục đang mở mới nhất")
    c.add_argument("--outcome", required=True, choices=["kept", "reverted", "superseded"])
    c.add_argument("--why", required=True, help="bằng chứng đã kết luận")
    c.add_argument("--promoted", required=True,
                   help="test ID / ADR-00NN / skill nào / none — bắt buộc trả lời")
    c.set_defaults(func=cmd_close)

    i = sub.add_parser("index"); i.set_defaults(func=cmd_index)

    l = sub.add_parser("list")
    l.add_argument("--kind"); l.add_argument("--area"); l.add_argument("--id")
    l.add_argument("--plan")
    l.add_argument("--open", action="store_true")
    l.set_defaults(func=cmd_list)

    pl = sub.add_parser("plan", help="quản lý plan (vòng ngoài SDD)")
    psub = pl.add_subparsers(dest="plancmd", required=True)

    pn = psub.add_parser("new", help="mở plan mới: spec · clarify · plan · tasks")
    pn.add_argument("name")
    pn.add_argument("--milestone", required=True)
    pn.add_argument("--covers", required=True, help="test ID, phân tách bằng dấu phẩy")
    pn.add_argument("--adr", help="ADR làm căn cứ, ví dụ 0005")
    pn.add_argument("--requirements", help="mục nguồn trong docs/product/, phân tách bằng dấu phẩy")
    pn.set_defaults(func=cmd_plan_new)

    pls = psub.add_parser("list"); pls.set_defaults(func=cmd_plan_list)

    pk = psub.add_parser("lock", help="chốt một artifact (gate tuần tự)")
    pk.add_argument("name"); pk.add_argument("artifact", choices=LOCK_ORDER)
    pk.set_defaults(func=cmd_plan_lock)

    ps_ = psub.add_parser("sync", help="tick lại tasks.md từ tracker + sinh STATUS.md")
    ps_.add_argument("name", nargs="?")
    ps_.set_defaults(func=cmd_plan_sync)

    pf = psub.add_parser("freeze", help="feature đóng — plan thành bất biến")
    pf.add_argument("name"); pf.add_argument("--force", action="store_true")
    pf.set_defaults(func=cmd_plan_freeze)

    s = sub.add_parser("show"); s.add_argument("entry"); s.set_defaults(func=cmd_show)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
