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

# Đảo lại được không. Đây là field quyết định mức độ cẩn trọng cần có, và là thứ
# duy nhất trong bản tin trả lời được câu "quyết định này có đáng tranh luận lại
# hay không": `no` thì tranh luận lại là vô nghĩa, `costly` thì phải cân, `yes`
# thì cứ thử.
REVERSIBLE = ["yes", "costly", "no"]
# Ai quyết. `source` nói ai GHI; cái này nói ai QUYẾT — hai chuyện khác nhau, và
# constitution #9 chỉ ràng buộc chuyện thứ hai.
DECIDERS = ["agent", "founder", "agent+founder", "hook"]

BODY_MAX = 30          # dòng thân tối đa; dài hơn thì nó là ADR hoặc test, không phải nhật ký
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
# Tên file mở đầu bằng mốc thời gian UTC, cùng dạng với `docs/evidence/ci/` — một
# quy ước cho mọi thứ có dấu thời gian trong repo, không phải hai. Đổi lại: `ls`
# đọc ra được dòng thời gian của phiên mà không cần mở file nào, và thứ tự file
# trên đĩa trùng thứ tự sự việc.
STAMP = r"\d{4}-\d{2}-\d{2}T\d{6}Z"
ID_RE = re.compile(rf"^{STAMP}-S(\d{{4}})-")


def sh(*a, default=""):
    try:
        r = subprocess.run(a, capture_output=True, text=True, cwd=ROOT, timeout=15)
        return r.stdout.strip() if r.returncode == 0 else default
    except Exception:
        return default


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp(iso):
    """`2026-08-23T06:37:15Z` -> `2026-08-23T063715Z` — bỏ ':' vì Windows cấm ký
    tự đó trong tên file. Giống hệt cách track.py đặt tên thư mục evidence."""
    return iso.replace(":", "")


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


def ids_on_all_branches():
    """ID đã cấp trên MỌI nhánh — kể cả nhánh chưa merge, remote đã fetch, và mục
    về sau bị xoá.

    `max(id trong cây làm việc) + 1` chỉ đúng khi một mình một nhánh. Hai nhánh mở
    song song thì cả hai cấp `S0008`, và lúc merge có hai mục khác nhau cùng một id
    — mà id chính là thứ `supersedes` trỏ tới, nên chuỗi truy vết đứt đúng ở chỗ nó
    cần liền nhất. Quét git rẻ hơn nhiều so với gỡ một lần trùng id.
    """
    out = set()
    log = sh("git", "log", "--all", "--pretty=format:", "--name-only",
             "--diff-filter=A", "--", ".steering/entries")
    for line in log.splitlines():
        m = ID_RE.match(os.path.basename(line.strip()))
        if m:
            out.add(int(m.group(1)))
    return out


def next_id():
    used = {int(ID_RE.match(os.path.basename(p)).group(1)) for p in paths()}
    used |= ids_on_all_branches()
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

## Đã cân nhắc
{alts}

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

    rev = getattr(a, "reversible", None) or "yes"
    if rev not in REVERSIBLE:
        sys.exit(f"--reversible phải là một trong: {', '.join(REVERSIBLE)}")
    dec_by = getattr(a, "deciders", None) or ("hook" if a.source == "hook" else "agent")
    if dec_by not in DECIDERS:
        sys.exit(f"--deciders phải là một trong: {', '.join(DECIDERS)}")
    decision = getattr(a, "decision", None) or ""
    # `kind: decision` mà không nói được quyết định là gì thì nó là ghi chép, không
    # phải quyết định — và sáu tháng sau không ai suy lại được từ phần thân.
    if a.kind == "decision" and not decision:
        sys.exit("--kind decision thì bắt buộc --decision \"<câu quyết định, thể "
                 "khẳng định: 'tên file steering mở đầu bằng mốc UTC'>\"")
    revisit = getattr(a, "revisit", None) or ""
    if revisit and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", revisit):
        sys.exit("--revisit phải là ngày dạng YYYY-MM-DD")

    plan = a.plan or ""
    if not plan:
        # Tự gắn khi KHÔNG nhập nhằng: đúng một plan đang mở trên nhánh này.
        # Mục quên `plan:` thì rơi ra ngoài JOURNAL.md của feature, và lời hứa
        # "plan với nhật ký nằm cạnh nhau" thành lời hứa suông — mà quên là chuyện
        # thường, nên chỗ này để máy nhớ thay.
        cur = sh("git", "rev-parse", "--abbrev-ref", "HEAD", default="?")
        cands = [n for n in plan_names()
                 if not plan_fm(n).get("closed")
                 and plan_fm(n).get("branch", "").strip() == cur]
        if len(cands) == 1:
            plan = cands[0]
            print(f"(tự gắn --plan {plan} — plan duy nhất đang mở trên nhánh {cur})",
                  file=sys.stderr)
    if plan and plan not in plan_names():
        sys.exit(f"plan {plan!r} không có trong .steering/plans/. "
                 f"Có: {', '.join(plan_names()) or '(chưa có plan nào)'}")

    sid = next_id()
    ts = now()
    os.makedirs(ENTRIES, exist_ok=True)
    # Một mốc thời gian dùng cho CẢ tên file lẫn frontmatter. Gọi now() hai lần thì
    # hai chỗ lệch nhau vài giây, và `./mo trace` sẽ bắt đúng cái lệch đó.
    path = os.path.join(ENTRIES, f"{stamp(ts)}-{sid}-{a.kind}-{slug(a.title)}.md")

    fm = [
        "---",
        f"id: {sid}",
        f"date: {ts}",
        f"kind: {a.kind}",
        f"outcome: {a.outcome}",
        f"title: {q(a.title)}",
        f"decision: {q(decision)}",
        f"reversible: {rev}",
        f"deciders: {dec_by}",
        f"revisit: {revisit}",
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
            alts=bullets(getattr(a, "alt", None),
                         "- <phương án khác đã nghĩ tới — và vì sao không chọn. "
                         "Không có thì ghi rõ: 'không có phương án nào khác'>"),
            did=bullets(a.did, "- <file / lệnh cụ thể>"),
            proof=a.proof or "<quan sát đã kết luận: file:dòng, output lệnh, dòng log "
                             "— không phải cảm nhận>",
        )
    open(path, "w", encoding="utf-8").write("\n".join(fm) + body)
    rebuild_index()
    print(f"{sid}  {os.path.relpath(path, ROOT)}")
    return path


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
    close_entry(path, a.outcome, a.why, a.promoted)
    rebuild_index()
    print(f"{fm.get('id')}  {a.outcome}  → {a.promoted}")


def close_entry(path, outcome, why, promoted):
    """Đóng một mục. Tách khỏi cmd_close để `plan abandon` gọi lại được —
    quyết định bỏ một plan phải nằm trong nhật ký như mọi quyết định khác."""
    text = open(path, encoding="utf-8").read()
    text = re.sub(r"^outcome: .*$", f"outcome: {outcome}", text, count=1, flags=re.M)
    text = re.sub(r"^promoted_to: .*$", f"promoted_to: {q(promoted)}", text, count=1, flags=re.M)
    text = text.replace(
        "## Kết luận\n<điền khi đóng>",
        f"## Kết luận\n**{outcome}** — {why}\n\n"
        f"_Đóng {now()} · commit `{sh('git', 'rev-parse', '--short', 'HEAD', default='?')}`_",
    )
    text = re.sub(r"## Đã nâng thành\n<điền khi đóng[^>]*>",
                  f"## Đã nâng thành\n{promoted}", text)
    open(path, "w", encoding="utf-8").write(text)


# ------------------------------------------------------------------ index

def rebuild_index():
    rows = []
    for p in paths():
        fm = parse_fm(p)
        rows.append({**fm, "file": os.path.basename(p)})
    rows.sort(key=lambda r: r.get("id", ""), reverse=True)

    # Ai thay ai: suy từ `supersedes:` của plan MỚI, không ghi ngược vào plan cũ —
    # plan cũ có thể đã frozen, mà frozen nghĩa là không sửa được nữa.
    replaced_by = {}
    for n in plan_names():
        for old in re.findall(r"[\w.-]+", plan_fm(n).get("supersedes", "")):
            replaced_by.setdefault(old, []).append(n)

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
        live = [n for n in plan_names() if not plan_fm(n).get("closed")]
        dead = [n for n in plan_names() if plan_fm(n).get("closed")]
        head = ["| Plan | Milestone | Trạng thái | Covers | ADR | Bị thay bởi | Nhật ký |",
                "|---|---|---|---|---|---|---|"]

        def row(name, closed=False):
            pf = plan_fm(name)
            n_j = sum(1 for r in rows if r.get("plan") == name)
            state = (f"**{pf.get('closed_as', 'đóng')}** · {pf.get('closed', '')[:10]}"
                     if closed else gate_summary(name))
            by = ", ".join(f"[{x}](plans/{x}/)" for x in replaced_by.get(name, [])) or "—"
            return (f"| [{name}](plans/{name}/) | {pf.get('milestone', '—')} | {state} "
                    f"| {pf.get('covers', '[]').strip('[]') or '—'} "
                    f"| {pf.get('adr', '[]').strip('[]') or '—'} | {by} "
                    f"| [{n_j} mục](plans/{name}/JOURNAL.md) |")

        if live:
            L += ["## Plan đang mở", ""] + head + [row(n) for n in live] + [""]
        if dead:
            L += ["## Plan đã đóng — giữ nguyên, không xoá", "",
                  "> `frozen` = feature xong. `abandoned` = bỏ giữa đường — lý do ở "
                  "`why_closed:` trong `spec.md` và ở mục nhật ký cùng plan.", ""]
            L += head + [row(n, closed=True) for n in dead] + [""]

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
    rebuild_history()
    for n in plan_names():
        rebuild_status(n)
    return len(rows)


def adr_events():
    """ADR cũng là quyết định — nó thuộc cùng một dòng thời gian.

    Để ngoài thì người truy vết phải ghép hai danh sách bằng đầu, và sẽ bỏ sót
    đúng chỗ quan trọng nhất: một mục nhật ký được nâng thành ADR.
    """
    d = os.path.join(ROOT, "docs", "adr")
    if not os.path.isdir(d):
        return []
    out = []
    for n in sorted(os.listdir(d)):
        if not re.match(r"^\d{4}-", n):
            continue
        text = open(os.path.join(d, n), encoding="utf-8").read()
        date = re.search(r"^-\s*Date:\s*(\d{4}-\d{2}-\d{2})", text, re.M)
        st = re.search(r"^-\s*Status:\s*(\S+)", text, re.M)
        title = re.search(r"^#\s*(.+)$", text, re.M)
        if not date:
            continue
        # ADR chỉ có ngày, không có giờ — gắn 00:00:00 để sắp cùng thang với mục nhật ký
        out.append((f"{date.group(1)}T00:00:00Z", "ADR",
                    f"[{title.group(1) if title else n}](../docs/adr/{n})"
                    f" · {st.group(1) if st else '?'}"))
    return out


def rebuild_history():
    """HISTORY.md — mọi quyết định của mọi phiên, xếp thành MỘT dòng thời gian.

    INDEX.md trả lời "bây giờ đang thế nào". File này trả lời "đã đi qua những
    gì" — hai câu hỏi khác nhau, và câu thứ hai là câu của người truy vết. Trạng
    thái hiện tại không nói được vì sao đã tới đây; chỉ chuỗi sự việc nói được.
    """
    ev = list(adr_events())

    for name in plan_names():
        pf = plan_fm(name)
        sup = pf.get("supersedes", "[]").strip("[]").strip()
        if pf.get("created"):
            ev.append((pf["created"], "plan",
                       f"mở plan **[{name}](plans/{name}/)** · {pf.get('milestone', '?')} "
                       f"· covers {pf.get('covers', '[]')}"
                       + (f" · thay cho `{sup}`" if sup else "")))
        cl = parse_fm(os.path.join(PLANS, name, "clarify.md"))
        if cl.get("answered") and cl["answered"] != "answered":
            ev.append((cl["answered"], "GATE NGƯỜI",
                       f"founder trả lời {cl.get('questions', '?')} câu clarify của "
                       f"[{name}](plans/{name}/)"))
        if pf.get("reviewed"):
            ev.append((pf["reviewed"], "triage",
                       f"xem lại và **giữ** plan [{name}](plans/{name}/) — "
                       f"{pf.get('reviewed_why', '')}"))
        for k in LOCK_ORDER:
            fm = parse_fm(os.path.join(PLANS, name, LOCK_FILE[k]))
            if fm.get("locked"):
                ev.append((fm["locked"], "cổng",
                           f"chốt `{k}.md` của [{name}](plans/{name}/)"))
        if pf.get("closed"):
            ev.append((pf["closed"], "plan",
                       f"**{pf.get('closed_as', 'đóng')}** plan [{name}](plans/{name}/)"
                       f" — {pf.get('why_closed', '')}"))

    for p in paths():
        fm, f = parse_fm(p), os.path.basename(p)
        extra = ""
        if fm.get("decision"):
            extra = f" · **quyết định:** {fm['decision']}"
        if fm.get("reversible") in ("costly", "no"):
            extra += f" · đảo lại: {fm['reversible']}"
        if fm.get("revisit"):
            extra += f" · xem lại {fm['revisit']}"
        ev.append((fm.get("date", ""), fm.get("kind", "?"),
                   f"mở [{fm.get('id')}](entries/{f}) — {fm.get('title')}{extra}"))
        m = re.search(r"_Đóng (\S+) ·", open(p, encoding="utf-8").read())
        if m:
            ev.append((m.group(1), fm.get("kind", "?"),
                       f"đóng [{fm.get('id')}](entries/{f}) **{fm.get('outcome')}** → "
                       f"{fm.get('promoted_to') or 'none'}"))

    ev.sort(key=lambda e: e[0], reverse=True)
    L = ["# .steering — dòng thời gian", "",
         "> ⚙️ Sinh bởi `tools/steering/steer.py` — **không sửa tay**. "
         "Trạng thái hiện tại: `INDEX.md`.",
         f"> {len(ev)} sự việc · plan · cổng chốt · mục nhật ký · ADR, mới nhất trên đầu", "",
         "| Mốc (UTC) | Loại | Việc |", "|---|---|---|"]
    L += [f"| `{t}` | {k} | {d} |" for t, k, d in ev]
    L.append("")
    open(os.path.join(STEER_DIR, "HISTORY.md"), "w", encoding="utf-8").write("\n".join(L))
    return len(ev)


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
    h = rebuild_history()
    print(f"steering: {n} mục · {m} plan · {h} sự việc "
          f"· INDEX.md + HISTORY.md + JOURNAL.md từng plan")


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


def _set_field(path, key, value):
    """Ghi một field vào frontmatter — thay nếu đã có, chèn nếu chưa.

    Plan trước đây chỉ ghi TRẠNG THÁI (`status: locked`) mà không ghi SỰ VIỆC:
    không ai biết cổng spec chốt lúc nào, plan đóng lúc nào. Không có mốc thì
    không có dòng thời gian, mà truy vết chính là đọc dòng thời gian.
    """
    t = open(path, encoding="utf-8").read()
    # `[ \t]*`, KHÔNG phải `\s*`: `\s` khớp cả xuống dòng, nên `^closed:\s*.*$`
    # nuốt luôn dòng `closed_as:` ngay dưới. Đã dính đúng lỗi này — mất field
    # `covers:` của spec.md mà không có gì kêu, tới lúc `./mo trace` báo
    # "covers rỗng" mới lộ.
    if re.search(rf"^{key}:[ \t]*.*$", t, flags=re.M):
        t = re.sub(rf"^{key}:[ \t]*.*$", f"{key}: {value}", t, count=1, flags=re.M)
    else:
        m = FM_RE.match(t)
        if not m:
            return
        t = t[:m.end(1)] + f"\n{key}: {value}" + t[m.end(1):]
    open(path, "w", encoding="utf-8").write(t)


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
    icon = {"draft": "✏️", "locked": "🔒", "open": "❓", "answered": "✅",
            "frozen": "🧊", "abandoned": "🚫"}

    L = [f"# {name} — trạng thái", "",
         "> ⚙️ Máy sinh (`./mo steer plan sync`) — **không sửa tay**.",
         f"> Milestone **{fm.get('milestone', '?')}** · "
         f"ADR {fm.get('adr', '[]')} · nguồn: xem `spec.md`", ""]
    if fm.get("closed"):
        # Mở STATUS.md của một plan đã chết mà không thấy ngay là chết thì sẽ có
        # người làm tiếp theo nó.
        L += [f"> 🚫 **Plan này đã {fm.get('closed_as', 'đóng')}** lúc "
              f"`{fm.get('closed')}` — {fm.get('why_closed', '')}",
              ">", "> Giữ lại để truy vết, không làm tiếp. "
              "Nhật ký lý do: `JOURNAL.md`.", ""]
    L += ["## Cổng chốt", "",
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
    rebuild_history()
    print(f"steering: đồng bộ {len(names)} plan (tasks.md tick lại từ tracker, STATUS.md sinh lại)")


def cmd_plan_lock(a):
    if a.artifact not in LOCK_ORDER:
        sys.exit(f"artifact phải là một trong: {', '.join(LOCK_ORDER)}")
    d = os.path.join(PLANS, a.name)
    if not os.path.isdir(d):
        sys.exit(f"không có plan {a.name!r}")
    if plan_fm(a.name).get("closed"):
        sys.exit(f"{a.name} đã đóng ({plan_fm(a.name).get('closed_as')}) — "
                 "không chốt thêm cổng nào. Mở plan mới với --supersedes nếu làm lại.")
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
        # Đáp án của founder là quyết định của NGƯỜI — nó phải có mốc để vào dòng
        # thời gian, không thì loại quyết định quan trọng nhất lại là loại duy nhất
        # không truy vết được thời điểm.
        _set_field(cl, "answered", now())
        _set_field(cl, "questions", str(len(re.findall(r"^###\s", body, re.M))))

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
    _set_field(path, "locked", now())        # sự việc, không chỉ trạng thái
    rebuild_status(a.name)
    rebuild_index()
    nxt = LOCK_ORDER[i + 1] if i + 1 < len(LOCK_ORDER) else None
    print(f"{a.name}/{fn}: 🔒 locked"
          + (f" — tiếp theo chốt `{nxt}`" if nxt else " — cả bốn cổng đã chốt, vào /task được"))


def check_contract_path(c):
    """`contract:` chỉ khai file/thư mục trong `specs/`.

    Hợp đồng là thứ duy nhất bên ngoài đọc được (agent, protocol, probe là phần
    open source). Cho khai đường dẫn ngoài `specs/` thì field này biến thành "danh
    sách file tôi sẽ sửa" — vô nghĩa, vì đó là việc của git diff.
    """
    if not c.startswith("specs/"):
        sys.exit(f"contract chỉ nhận đường dẫn trong specs/ — không hợp lệ: {c}")
    p = os.path.join(ROOT, c)
    if c.endswith("/"):
        if not os.path.isdir(p):
            sys.exit(f"contract trỏ thư mục không tồn tại: {c}")
    elif not os.path.exists(p):
        # Không chặn: plan có quyền khai file hợp đồng nó sẽ TẠO.
        print(f"(chú ý: {c} chưa tồn tại — plan sẽ tạo?)", file=sys.stderr)


def cmd_plan_contract(a):
    """Thêm file hợp đồng vào scope của plan — kể cả khi spec đã chốt.

    Cửa này phải mở được: lúc implement mới phát hiện phải sửa thêm một schema là
    chuyện thật. Nhưng nó không được mở IM LẶNG — mở rộng scope hợp đồng sau khi
    chốt spec là quyết định, nên nó sinh một mục nhật ký.
    """
    d = os.path.join(PLANS, a.name)
    if not os.path.isdir(d):
        sys.exit(f"không có plan {a.name!r}")
    spec = os.path.join(d, "spec.md")
    cur = [x for x in re.split(r"[,\s]+", plan_fm(a.name).get("contract", "").strip("[]")) if x]
    if a.list:
        print("\n".join(cur) or "(chưa khai file hợp đồng nào)")
        return
    if plan_fm(a.name).get("closed"):
        sys.exit(f"{a.name} đã đóng ({plan_fm(a.name).get('closed_as')}) — mở plan mới.")
    if not a.add:
        sys.exit("cần --add <đường dẫn trong specs/> hoặc --list")
    if file_status(a.name, "spec.md") in ("locked", "frozen") and not a.why.strip():
        sys.exit("spec.md đã chốt → mở rộng hợp đồng là quyết định, bắt buộc --why "
                 "\"vì sao lúc chốt spec chưa thấy file này\".")

    add = [x.strip().replace("\\", "/") for x in a.add.split(",") if x.strip()]
    for c in add:
        check_contract_path(c)
    new = [c for c in add if c not in cur]
    if not new:
        print(f"{a.name}: đã khai sẵn {', '.join(add)} — không đổi gì")
        return
    _set_field(spec, "contract", "[" + ", ".join(cur + new) + "]")

    locked = file_status(a.name, "spec.md") in ("locked", "frozen")
    if locked:
        path = new_entry(
            kind="decision", area="specs", plan=a.name, deciders="agent",
            reversible="costly",
            title=f"Mo rong hop dong cua {a.name}",
            decision=f"them {', '.join(new)} vao contract cua {a.name}",
            context=f"spec.md của {a.name} đã chốt mà lúc implement mới thấy phải "
                    f"sửa thêm file hợp đồng.",
            why="Khi chốt spec đã tin rằng danh sách file hợp đồng là đủ.",
            alt="mở plan mới cho phần hợp đồng thêm — bỏ vì cùng một hành vi, tách "
                "ra thì covers trùng nhau",
            did=f"./mo steer plan contract {a.name} --add {','.join(new)}",
            proof=a.why)
        close_entry(path, "kept", a.why, "none")
    rebuild_index()
    print(f"{a.name}: contract += {', '.join(new)}"
          + ("  (spec đã chốt → đã ghi nhật ký)" if locked else ""))


def cmd_plan_new(a):
    name = slug(a.name, 48)
    d = os.path.join(PLANS, name)
    if os.path.isdir(d):
        sys.exit(f"plan {name!r} đã tồn tại")

    sup = [s.strip() for s in (getattr(a, "supersedes", None) or "").split(",") if s.strip()]
    for s in sup:
        if s not in plan_names():
            sys.exit(f"--supersedes trỏ plan không tồn tại: {s}. "
                     f"Có: {', '.join(plan_names()) or '(chưa có plan nào)'}")

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
    contract = [x.strip().replace("\\", "/") for x in (a.contract or "").split(",") if x.strip()]
    for c in contract:
        check_contract_path(c)

    ts = now()
    os.makedirs(d)
    for fn, (what, body) in PLAN_FILES.items():
        # `status` là của TỪNG artifact, không phải của cả plan: spec chốt trước,
        # plan chốt sau, tasks chốt cuối. Chốt cả cụm một lần thì gate tuần tự
        # của SDD không tồn tại.
        st = "answered" if fn == "clarify.md" else "draft"
        fm = ["---", f"plan: {name}", f"milestone: {a.milestone}", f"status: {st}",
              f"created: {ts}"]
        if fn == "spec.md":
            # Vòng đời của cả plan khai ở MỘT chỗ — spec.md. Khai ở năm file thì
            # có năm phiên bản sự thật về việc plan này còn sống hay đã chết.
            # `supersedes` chỉ trỏ một chiều (plan mới trỏ plan cũ); chiều ngược
            # do máy suy ra, vì plan cũ có thể đã đóng băng và không sửa được nữa.
            fm += [f"contract: [{', '.join(contract)}]",
                   f"supersedes: [{', '.join(sup)}]",
                   f"branch: {sh('git', 'rev-parse', '--abbrev-ref', 'HEAD', default='?')}",
                   "reviewed:", "reviewed_why:",
                   "closed:", "closed_as:", "why_closed:"]
        fm += [f"covers: [{', '.join(covers)}]", f"adr: [{', '.join(adr)}]", "requirements:"]
        fm += [f"  - {r}" for r in reqs] or ["  - <điền nguồn yêu cầu>"]
        fm += ["---", "", f"# {name} · {fn.replace('.md', '')} — {what}", ""]
        open(os.path.join(d, fn), "w", encoding="utf-8").write("\n".join(fm + body) + "\n")
    # clarify chưa trả lời thì chưa phải "answered"
    _set_status(os.path.join(d, "clarify.md"), "open")

    rebuild_index()
    print(f"{name}  .steering/plans/{name}/")
    print("  spec · clarify · plan · testcases · tasks   (+ STATUS.md, JOURNAL.md máy sinh)")
    print("Bước tiếp: điền spec.md rồi clarify.md, DỪNG chờ founder trả lời.")


STALE_DAYS = 14          # im lặng bao lâu thì coi là lạc
CLARIFY_DAYS = 7         # treo ở gate người bao lâu thì phải hỏi lại


def days_since(iso):
    if not iso:
        return None
    try:
        t = dt.datetime.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None
    return (dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) - t).days


def known_branches():
    out = set()
    for line in sh("git", "branch", "--all", "--format=%(refname:short)").splitlines():
        b = line.strip()
        if b:
            out.add(b)
            out.add(b.split("/", 1)[-1] if b.startswith("origin/") else b)
    return out


def triage():
    """Plan/quyết định đang ở trạng thái CẦN NGƯỜI QUYẾT.

    Bốn hệ hồ sơ đều trả lời được "cái gì đang có". Không hệ nào trả lời
    "cái gì đang treo mà không ai nhớ" — và đó chính là chỗ plan đi lạc: không bị
    xoá, không bị đóng, chỉ im lặng trôi ra khỏi tầm nhìn cho tới khi có người mở
    lại nhánh cũ. Hàm này đi tìm đúng loại im lặng đó.

    Trả về danh sách dict: plan/entry · vì sao · hai lệnh để chọn.
    """
    items = []
    passing = tracker_pass()
    branches = known_branches()
    open_ms = open_milestone()
    ms_num = int(re.sub(r"\D", "", open_ms) or 0)

    for name in plan_names():
        pf = plan_fm(name)
        if pf.get("closed"):
            continue
        acts = [pf.get("created", ""), pf.get("reviewed", "")]
        acts += [parse_fm(os.path.join(PLANS, name, LOCK_FILE[k])).get("locked", "")
                 for k in LOCK_ORDER]
        acts += [parse_fm(p).get("date", "") for p in paths()
                 if parse_fm(p).get("plan") == name]
        last = max([x for x in acts if x] or [""])
        idle = days_since(last)
        why = []

        br = pf.get("branch", "").strip()
        if br and br not in ("?", "main") and br not in branches:
            why.append(f"nhánh `{br}` không còn tồn tại — plan mồ côi")

        covers = TID_RE.findall(pf.get("covers", ""))
        if covers and all(passing.get(i) for i in covers):
            why.append("mọi test ID trong covers đã XANH mà plan chưa đóng — "
                       "việc đã xong ở đâu đó khác, plan bị vượt")

        p_ms = int(re.sub(r"\D", "", pf.get("milestone", "") or "") or 0)
        if ms_num and p_ms and p_ms < ms_num:
            why.append(f"thuộc {pf.get('milestone')} mà milestone đang mở là {open_ms}")

        if file_status(name, "clarify.md") == "open" and (idle or 0) >= CLARIFY_DAYS:
            why.append(f"treo ở gate người (clarify) {idle} ngày")
        elif idle is not None and idle >= STALE_DAYS:
            why.append(f"im lặng {idle} ngày, chưa chốt cổng nào mới")

        if why:
            items.append({
                "what": f"plan {name}", "idle": idle, "why": why,
                "choices": [
                    f'./mo steer plan abandon {name} --why "..." [--next <plan>]',
                    f'./mo steer plan keep {name} --why "vẫn làm, lý do..."',
                ]})

    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    for p in paths():
        fm = parse_fm(p)
        rv = fm.get("revisit", "").strip()
        if rv and rv <= today:
            items.append({
                "what": f"{fm.get('id')} {fm.get('title', '')[:44]}", "idle": days_since(fm.get("date")),
                "why": [f"quyết định tạm, hẹn xem lại từ {rv} — đã tới hạn"],
                "choices": [f'./mo steer new --kind decision --supersedes {fm.get("id")} '
                            f'--decision "..." (quyết lại)',
                            f'sửa `revisit:` sang hạn mới nếu chưa quyết được']})

    seen = {}
    for p in paths():
        seen.setdefault(parse_fm(p).get("id"), []).append(os.path.basename(p))
    for sid, fs in seen.items():
        if len(fs) > 1:
            items.append({
                "what": f"id {sid} trùng ({len(fs)} mục)", "idle": None,
                "why": ["hai nhánh cấp cùng một id rồi merge — `supersedes` trỏ tới "
                        "id này thành nhập nhằng"],
                "choices": [f"./mo steer renumber <mốc thời gian của mục mở sau>"]})
    return items


def cmd_plan_triage(a):
    items = triage()
    if a.cache:
        # Hook SessionStart đọc cache này. Nó phải chạy được khi Docker chưa lên,
        # nên không thể tự gọi python — cùng cách statusline đọc progress.txt.
        os.makedirs(os.path.dirname(os.path.abspath(a.cache)), exist_ok=True)
        with open(a.cache, "w", encoding="utf-8") as f:
            for it in items:
                f.write(f"{it['what']} :: {'; '.join(it['why'])} :: {it['choices'][0]}\n")
    if not a.quiet:
        if not items:
            print("triage: không có gì treo — mọi plan đang mở đều còn dấu hiệu sống")
        else:
            print(f"⚠️  {len(items)} thứ cần NGƯỜI quyết:\n")
            for it in items:
                print(f"  ▸ {it['what']}")
                for w in it["why"]:
                    print(f"      · {w}")
                for c in it["choices"]:
                    print(f"      → {c}")
                print()
    if items and a.strict:
        sys.exit(1)


def cmd_plan_keep(a):
    """"Vẫn làm tiếp" cũng là một câu trả lời — và nó phải để lại dấu, nếu không
    triage sẽ hỏi lại đúng câu đó mỗi phiên cho tới khi người ta thôi đọc."""
    d = os.path.join(PLANS, a.name)
    if not os.path.isdir(d):
        sys.exit(f"không có plan {a.name!r}")
    if plan_fm(a.name).get("closed"):
        sys.exit(f"{a.name} đã đóng ({plan_fm(a.name).get('closed_as')}) — không giữ lại được.")
    spec = os.path.join(d, "spec.md")
    _set_field(spec, "reviewed", now())
    _set_field(spec, "reviewed_why", q(a.why))
    _set_field(spec, "branch", sh("git", "rev-parse", "--abbrev-ref", "HEAD", default="?"))
    rebuild_index()
    print(f"{a.name}: vẫn mở, đã xem lại lúc {now()} — im lặng {STALE_DAYS} ngày nữa "
          "thì triage hỏi lại")


def cmd_plan_list(a):
    if not plan_names():
        print("(chưa có plan nào — ./mo steer plan new <ten> --milestone M3 --covers ...)")
        return
    for n in plan_names():
        pf = plan_fm(n)
        n_j = sum(1 for p in paths() if parse_fm(p).get("plan") == n)
        state = pf.get("closed_as") or gate_summary(n)
        print(f"{n:24} {pf.get('milestone', '?'):4} {state:12} "
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
    spec = os.path.join(d, "spec.md")
    _set_field(spec, "closed", now())
    _set_field(spec, "closed_as", "frozen")
    _set_field(spec, "why_closed", q(a.why or "feature hoàn tất, bốn cổng đã chốt"))
    rebuild_index()
    print(f"{a.name}: frozen — từ giờ bất biến, đổi ý thì mở plan mới")


def new_entry(**kw):
    """Mở một mục nhật ký từ trong code (không qua CLI). Trả về đường dẫn mục vừa mở."""
    ns = argparse.Namespace(kind="decision", title="", area="flow", ids=None, context=None,
                            why=None, did=None, proof=None, supersedes=None, plan=None,
                            outcome="open", source="agent", command=None)
    for k, v in kw.items():
        setattr(ns, k, v)
    # Lấy đường dẫn từ chính cmd_new. Trước đây đoán bằng `paths()[-1]` ("mốc mới
    # nhất") — sai ngay khi trong thư mục có mục mang mốc muộn hơn, ví dụ mục vừa
    # merge từ nhánh khác: close_entry sẽ đóng NHẦM mục của người khác.
    return cmd_new(ns)


def cmd_plan_abandon(a):
    """Bỏ một plan mà KHÔNG xoá nó.

    Trước lệnh này, plan chỉ có ba trạng thái: draft → locked → frozen, và `freeze`
    đòi cả bốn cổng đã chốt. Nghĩa là một plan bị bỏ giữa đường không có cửa ra
    hợp lệ nào — cách duy nhất là `rm -rf` thư mục. Thư mục xoá thì không để lại
    gì: không tên, không lý do, không cả một dòng trong git nếu chưa từng commit.
    Đó là đúng loại mất mát mà `.steering/` sinh ra để chống.
    """
    d = os.path.join(PLANS, a.name)
    if not os.path.isdir(d):
        sys.exit(f"không có plan {a.name!r}. Có: {', '.join(plan_names()) or '(chưa có)'}")
    fm = plan_fm(a.name)
    if fm.get("closed"):
        sys.exit(f"{a.name} đã đóng rồi ({fm.get('closed_as')} lúc {fm.get('closed')}). "
                 "Mở plan mới với --supersedes nếu muốn làm lại hướng này.")

    for fn in list(PLAN_FILES):
        p = os.path.join(d, fn)
        if os.path.exists(p):
            _set_status(p, "abandoned")
    spec = os.path.join(d, "spec.md")
    _set_field(spec, "closed", now())
    _set_field(spec, "closed_as", "abandoned")
    _set_field(spec, "why_closed", q(a.why))

    path = new_entry(
        kind="decision", area=a.area, plan=a.name,
        title=f"Bo plan {a.name}",
        context=f"Plan {a.name} dừng giữa đường. Thư mục vẫn nằm nguyên ở "
                f".steering/plans/{a.name}/ với status: abandoned — bỏ một hướng đi "
                f"là quyết định, và quyết định thì phải đọc lại được sáu tháng sau.",
        why=f"Khi mở plan này đã tin rằng đó là đường đúng cho "
            f"{fm.get('milestone', '?')}, cover {fm.get('covers', '[]')}.",
        did=f"./mo steer plan abandon {a.name} | 5 artifact -> status: abandoned "
            f"| spec.md -> closed_as: abandoned",
        proof=a.why,
    )
    close_entry(path, "kept", a.why, a.next or "none")
    rebuild_index()
    print(f"{a.name}: abandoned — thư mục giữ nguyên, lý do đã vào nhật ký"
          + (f", việc chuyển sang: {a.next}" if a.next else ""))


def cmd_renumber(a):
    """Cấp lại id cho một mục — CHỈ khi merge hai nhánh ra hai mục cùng id.

    Đây là ngoại lệ duy nhất của luật "mục đã đóng thì bất biến", nên nó không im
    lặng: mỗi lần đổi số sinh một mục nhật ký ghi lại việc đổi. Mốc thời gian trong
    tên file KHÔNG đổi — nó là lúc sự việc xảy ra, không phải lúc đánh số lại.
    """
    hit = [p for p in paths() if a.entry in os.path.basename(p)]
    if len(hit) != 1:
        sys.exit(f"không xác định được mục từ {a.entry!r} ({len(hit)} khớp). "
                 "Trùng id thì truyền cả mốc thời gian, ví dụ 2026-08-25T182903Z.\n"
                 + "\n".join("  " + os.path.basename(p) for p in hit))
    path = hit[0]
    old = parse_fm(path).get("id", "")
    new = next_id()

    text = open(path, encoding="utf-8").read()
    text = re.sub(r"^id: .*$", f"id: {new}", text, count=1, flags=re.M)
    text = text.replace(f"# {old} ·", f"# {new} ·", 1)
    open(path, "w", encoding="utf-8").write(text)
    newp = os.path.join(ENTRIES, os.path.basename(path).replace(f"-{old}-", f"-{new}-", 1))
    os.rename(path, newp)

    # Mục khác đang trỏ `supersedes: [S0008]` — KHÔNG tự sửa. Sau khi merge có hai
    # mục từng mang số đó, nên máy không biết được cái trỏ tới là cái nào; đoán sai
    # còn tệ hơn để người đọc quyết.
    # Chỉ báo mục THAM CHIẾU tới số cũ. Mục cùng số kia nhắc "S0008" vì đó là id
    # của chính nó — báo cả nó thì cảnh báo thành tiếng ồn, và tiếng ồn thì không
    # ai đọc.
    mentions = [os.path.basename(p) for p in paths()
                if p != newp and old and parse_fm(p).get("id") != old
                and old in open(p, encoding="utf-8").read()]

    p2 = new_entry(kind="decision", area="flow", deciders="agent", reversible="yes",
                   title=f"Danh so lai {old} thanh {new}",
                   decision=f"muc {old} doi thanh {new} de go trung id sau merge",
                   context=f"Merge hai nhánh ra hai mục cùng id {old}. Id là thứ "
                           f"`supersedes` trỏ tới, nên trùng id là chuỗi truy vết đứt.",
                   why=f"Tin rằng mục {old} này là mục mở sau, nên nó nhường số.",
                   alt="giữ nguyên và sống với trùng id — bỏ vì trace chặn, và "
                       "`steer show` không phân biệt được | sửa mốc thời gian cho "
                       "khác — bỏ vì mốc là sự thật về lúc xảy ra, không phải khoá",
                   did=f"./mo steer renumber {a.entry} | {os.path.basename(newp)}",
                   proof=f"trace: id trùng -> exit 2 trước khi đổi; sau khi đổi -> OK")
    close_entry(p2, "kept", f"{old} -> {new}, mốc thời gian giữ nguyên", "none")
    rebuild_index()

    print(f"{old} -> {new}   {os.path.basename(newp)}")
    if mentions:
        print("⚠️  còn nhắc tới " + old + " (KIỂM BẰNG MẮT, máy không tự sửa vì "
              "sau merge có hai mục từng mang số này):")
        for m in mentions:
            print("   " + m)


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
    n.add_argument("--decision", help="câu quyết định, thể khẳng định — BẮT BUỘC với --kind decision")
    n.add_argument("--alt", help="phương án đã cân nhắc và vì sao không chọn; "
                                "nhiều mục phân tách bằng ' | '")
    n.add_argument("--reversible", choices=REVERSIBLE, help="đảo lại được không (mặc định yes)")
    n.add_argument("--deciders", choices=DECIDERS, help="ai QUYẾT (khác --source: ai GHI)")
    n.add_argument("--revisit", help="YYYY-MM-DD — quyết định tạm, hẹn xem lại; "
                                    "triage sẽ nhắc khi tới hạn")
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
    pn.add_argument("--supersedes", help="plan cũ mà plan này thay cho, ví dụ m1-provisioning")
    pn.add_argument("--contract", help="file/thư mục trong specs/ mà plan sẽ chạm, "
                                      "phân tách bằng dấu phẩy (thư mục kết thúc bằng /)")
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
    pf.add_argument("--why", help="vì sao đóng (mặc định: feature hoàn tất)")
    pf.set_defaults(func=cmd_plan_freeze)

    pc = psub.add_parser("contract", help="khai thêm file specs/ vào scope của plan")
    pc.add_argument("name")
    pc.add_argument("--add", help="đường dẫn trong specs/, phân tách bằng dấu phẩy")
    pc.add_argument("--why", default="", help="vì sao mở rộng — bắt buộc nếu spec đã chốt")
    pc.add_argument("--list", action="store_true")
    pc.set_defaults(func=cmd_plan_contract)

    pt = psub.add_parser("triage", help="plan/quyết định đang treo, cần người quyết")
    pt.add_argument("--strict", action="store_true", help="exit 1 nếu có thứ đang treo (CI)")
    pt.add_argument("--cache", help="ghi dạng gọn ra file cho hook SessionStart đọc")
    pt.add_argument("--quiet", action="store_true")
    pt.set_defaults(func=cmd_plan_triage)

    pkp = psub.add_parser("keep", help='trả lời triage: "vẫn làm tiếp"')
    pkp.add_argument("name")
    pkp.add_argument("--why", required=True, help="vì sao vẫn giữ — bắt buộc")
    pkp.set_defaults(func=cmd_plan_keep)

    pa = psub.add_parser("abandon", help="bỏ plan giữa đường — KHÔNG xoá thư mục")
    pa.add_argument("name")
    pa.add_argument("--why", required=True,
                    help="vì sao bỏ — bắt buộc, đây là thứ duy nhất người sau đọc được")
    pa.add_argument("--next", help="plan / ADR / test ID làm thay; để trống = none")
    pa.add_argument("--area", default="flow", choices=AREAS)
    pa.set_defaults(func=cmd_plan_abandon)

    rn = sub.add_parser("renumber", help="cấp lại id khi merge ra hai mục cùng id")
    rn.add_argument("entry", help="mốc thời gian hoặc tên file của mục đổi số")
    rn.set_defaults(func=cmd_renumber)

    s = sub.add_parser("show"); s.add_argument("entry"); s.set_defaults(func=cmd_show)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
