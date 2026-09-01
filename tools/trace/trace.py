#!/usr/bin/env python3
"""
trace.py — traceability check (Lớp 3, docs/product/06-spec-management.md).

Sáu nhiệm vụ:
1. Mỗi test ID trong catalog phải xuất hiện ở >=1 file spec (dòng covers:)
   và >=1 file test Go (naming Test<ID bỏ gạch>_...). ID mồ côi = CẢNH BÁO.
   covers: trỏ tới ID không có trong catalog = LỖI (chặn typo).
2. Skill frontmatter `metadata.adr: [NNNN, ...]` — ADR không tồn tại hoặc đã
   superseded mà skill chưa cập nhật = LỖI (luật đồng bộ skill<->ADR).
3. CATALOG (track.py) khớp bảng ID trong 05-test-catalog.md, cả hai chiều = LỖI.
   MILESTONE trong track.py khớp tiêu đề nhóm trong file đó = LỖI nếu lệch.
4. Frontmatter của mọi skill/rule là YAML hợp lệ, key có thật, rule có `paths:`.
5. Nhật ký .steering/ truy vết được: INDEX khớp entries, test_ids có thật,
   promoted_to điền khi đóng; mục còn `open` = CẢNH BÁO.
6. Plan .steering/plans/ nối đúng: covers -> catalog, adr -> ADR chưa supersede,
   tasks.md không dùng ID ngoài covers.

Exit 0 nếu chỉ có cảnh báo; exit 1 nếu có lỗi.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "testtrack"))
from track import CATALOG, GROUPS, MILESTONE, norm_id  # một nguồn sự thật, không parse lại catalog md

CATALOG_MD = os.path.join("docs", "product", "05-test-catalog.md")

# Plan của feature đã chuyển từ specs/features/ sang .steering/plans/ — specs/ trở
# lại đúng vai hợp đồng máy-đọc-được, còn plan là quá trình. `covers:` ở cả hai nơi
# đều tính, nếu không thì dời nhà xong là mọi ID thành mồ côi.
SPEC_DIRS = ["specs", os.path.join("docs", "adr"), os.path.join(".steering", "plans")]
PLANS_DIR = os.path.join(".steering", "plans")
SKILL_DIR = os.path.join(".claude", "skills")
ADR_DIR = os.path.join("docs", "adr")

COVERS_RE = re.compile(r'"?[Cc]overs"?\s*:\s*\[?\s*"?([A-Z]{3}-\d{2}(?:[",\s]+[A-Z]{3}-\d{2})*)', re.M)
ID_IN_LIST_RE = re.compile(r"[A-Z]{3}-\d{2}")
# `adr:` nằm dưới `metadata:` trong frontmatter (chỗ dành cho key riêng của repo,
# theo spec skill). Cho phép thụt đầu dòng để bắt cả dạng cũ lẫn dạng mới.
ADR_FM_RE = re.compile(r"^\s*adr:\s*\[([0-9,\s]+)\]", re.M)


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
            # TEMPLATE.md chứa `covers:` làm ví dụ — tính nó vào thì ID trong ví dụ
            # trông như đã được spec cover, đúng kiểu hỏng im lặng trace sinh ra để chặn.
            if os.path.basename(path) == "TEMPLATE.md":
                continue
            text = open(path, encoding="utf-8").read()
            rel = os.path.relpath(path, ROOT)
            for m in COVERS_RE.finditer(text):
                for tid in ID_IN_LIST_RE.findall(m.group(1)):
                    found.setdefault(tid, []).append(rel)
    return found


TEST_FUNC_RE = re.compile(r"func\s+(Test\w+)\s*\(")
SUBTEST_RE = re.compile(r't\.Run\(\s*"([^"]*)"')


def collect_test_ids():
    """ID xuất hiện trong test Go: `func TestOTA07_...` HOẶC `t.Run("OTA-07 ...")`.

    Phải nhận dạng GIỐNG HỆT track.py, và đó là lý do nó import norm_id thay vì tự
    viết regex. track.py tick tracker bằng cách quét toàn bộ tên test mà `go test`
    in ra — gồm cả phần subtest. Chỗ này trước đây chỉ nhìn tên hàm, nên một test
    gộp-subtest (cách chính docstring của track.py khuyến khích) sẽ tick được tracker
    mà vẫn bị báo "chưa có test Go" mãi mãi: hai công cụ nói hai điều trái nhau về
    cùng một ID, và triệu chứng đó gần như không đoán ra được nguyên nhân.

    Chỉ quét khai báo hàm và chuỗi trong t.Run — KHÔNG quét cả file. Quét cả file
    thì một ID nhắc trong comment cũng thành "đã có test".
    """
    ids = set()
    for path in walk_files(".", ("_test.go",)):
        text = open(path, encoding="utf-8").read()
        for m in list(TEST_FUNC_RE.finditer(text)) + list(SUBTEST_RE.finditer(text)):
            tid = norm_id(m.group(1))
            if tid and tid in CATALOG:
                ids.add(tid)
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


SKILL_FM_KEYS = {
    "name", "description", "argument-hint", "arguments", "disable-model-invocation",
    "user-invocable", "allowed-tools", "disallowed-tools", "model", "effort",
    "context", "agent", "background", "hooks", "paths", "shell", "metadata",
    "license", "compatibility",
}


def check_frontmatter():
    """Frontmatter của skill/rule phải là YAML hợp lệ và chỉ dùng key có thật.

    Bẫy đã dính một lần: description không trích dẫn mà chứa "Trigger: ..." —
    dấu hai chấm giữa scalar làm YAML hỏng. Claude Code hiện đọc lỏng nên skill
    vẫn nạp được, nhưng đó là kiểu hỏng im lặng: nó sẽ vỡ ở phiên bản sau hoặc khi
    đóng gói skill, và không ai biết vì sao skill ngừng trigger.
    """
    import yaml  # chỉ trace cần yaml; giữ import cục bộ để các script khác không lệ thuộc

    errs = []
    targets = []
    skill_root = os.path.join(ROOT, SKILL_DIR)
    if os.path.isdir(skill_root):
        for n in sorted(os.listdir(skill_root)):
            p = os.path.join(skill_root, n, "SKILL.md")
            if os.path.exists(p):
                targets.append((p, True))
    rule_root = os.path.join(ROOT, ".claude", "rules")
    if os.path.isdir(rule_root):
        for n in sorted(os.listdir(rule_root)):
            if n.endswith(".md"):
                targets.append((os.path.join(rule_root, n), False))

    for path, is_skill in targets:
        rel = os.path.relpath(path, ROOT)
        text = open(path, encoding="utf-8").read()
        if not text.startswith("---"):
            errs.append(f"{rel}: thiếu frontmatter")
            continue
        try:
            fm = yaml.safe_load(text.split("---", 2)[1]) or {}
        except yaml.YAMLError as e:
            first = str(e).splitlines()[0]
            errs.append(f"{rel}: frontmatter không phải YAML hợp lệ — {first}. "
                        "Thường do dấu ':' trong description chưa trích dẫn.")
            continue
        if not isinstance(fm, dict):
            errs.append(f"{rel}: frontmatter phải là map")
            continue
        if is_skill:
            unknown = set(fm) - SKILL_FM_KEYS
            if unknown:
                errs.append(f"{rel}: key lạ trong frontmatter: {sorted(unknown)} "
                            "(key riêng của repo phải nằm dưới `metadata:`)")
            if not fm.get("description"):
                errs.append(f"{rel}: thiếu description — skill không trigger được")
        elif not fm.get("paths"):
            errs.append(f"{rel}: rule thiếu `paths:` — sẽ nạp vào MỌI phiên, "
                        "đúng thứ .claude/rules/ sinh ra để tránh")
    return errs


def check_steering():
    """Nhật ký .steering/ phải truy vết được: INDEX khớp entries, test ID có thật.

    Trả về (errors, warns). Mục `open` là CẢNH BÁO chứ không phải LỖI — mở một mục
    rồi chưa đóng là chuyện bình thường giữa chừng; chỉ đáng nhắc, không đáng chặn.
    """
    errs, warns = [], []
    entries_dir = os.path.join(ROOT, ".steering", "entries")
    index_md = os.path.join(ROOT, ".steering", "INDEX.md")
    if not os.path.isdir(entries_dir):
        return errs, warns

    KINDS = {"attempt", "wrong", "discovery", "decision", "risky"}
    AREAS = {"agent", "server", "protocol", "probe", "dashboard", "specs", "infra", "flow"}
    OUTCOMES = {"open", "kept", "reverted", "superseded"}
    BODY_MAX = 30
    # <mốc UTC>-<id>-<kind>-<slug>. Mốc đứng trước để `ls entries/` đọc ra được
    # dòng thời gian mà không phải mở file nào.
    sid_re = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{6}Z)-(S\d{4})-([a-z]+)-")

    # Plan đang mở, gom theo nhánh — để bắt mục nhật ký quên khai `plan:`.
    plans_by_branch = {}
    proot = os.path.join(ROOT, PLANS_DIR)
    for pn in (sorted(os.listdir(proot)) if os.path.isdir(proot) else []):
        sp = os.path.join(proot, pn, "spec.md")
        if not os.path.exists(sp):
            continue
        txt = open(sp, encoding="utf-8").read()
        pfm = {}
        if txt.startswith("---") and "\n---\n" in txt:
            for line in txt.split("\n---\n", 1)[0].lstrip("-\n").splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    pfm[k.strip()] = v.strip().strip('"')
        if not pfm.get("closed", "").strip():
            plans_by_branch.setdefault(pfm.get("branch", "").strip(), []).append(pn)

    names = sorted(n for n in os.listdir(entries_dir) if n.endswith(".md"))
    idx = open(index_md, encoding="utf-8").read() if os.path.exists(index_md) else ""

    seen_ids, open_n = {}, 0
    entries = {}

    for n in names:
        rel = f".steering/entries/{n}"
        m = sid_re.match(n)
        if not m:
            errs.append(f"{rel}: tên file phải theo dạng "
                        "2026-08-23T063715Z-S0007-<kind>-<slug>.md")
            continue

        text = open(os.path.join(entries_dir, n), encoding="utf-8").read()
        if not text.startswith("---") or "\n---\n" not in text:
            errs.append(f"{rel}: thiếu frontmatter")
            continue
        head, body = text.split("\n---\n", 1)
        fm = {}
        for line in head.lstrip("-\n").splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
        entries[fm.get("id", n)] = fm

        # id: duy nhất và khớp tên file — id là thứ mục khác trỏ tới, sai thì
        # cả chuỗi supersedes mất nghĩa.
        sid = fm.get("id", "")
        if sid != m.group(2):
            errs.append(f"{rel}: id trong frontmatter ({sid!r}) khác tên file ({m.group(2)})")
        if sid in seen_ids:
            errs.append(f"{rel}: id {sid} trùng với {seen_ids[sid]}")
        seen_ids[sid] = n
        if fm.get("kind") != m.group(3):
            errs.append(f"{rel}: kind trong frontmatter ({fm.get('kind')!r}) khác tên file")
        # Mốc trong tên file là thứ người đọc tin khi lướt `ls`. Nó lệch `date:`
        # nghĩa là file đã bị đổi tên bằng tay — tên nói dối về lúc sự việc xảy ra.
        if fm.get("date", "").replace(":", "") != m.group(1):
            errs.append(f"{rel}: mốc thời gian trong tên file khác `date:` "
                        f"({fm.get('date')!r}) — tên file do máy đặt, đừng sửa tay")

        if fm.get("kind") not in KINDS:
            errs.append(f"{rel}: kind không hợp lệ: {fm.get('kind')!r}")
        if fm.get("area") not in AREAS:
            errs.append(f"{rel}: area không hợp lệ: {fm.get('area')!r}")

        # Mục không khai `plan:` trong khi nhánh đó ĐANG có plan mở: nó rơi ra
        # ngoài JOURNAL.md của feature, nên mở thư mục plan ra sẽ không thấy thứ
        # đã thử rồi bỏ. Cảnh báo, không chặn — có quyết định thật sự không thuộc
        # feature nào (hạ tầng, quy trình), và đó là chuyện bình thường.
        # `flow` và `infra` là bộ máy của repo, không phải feature — quyết định ở
        # hai tầng đó không thuộc plan nào là chuyện bình thường, cảnh báo chúng
        # chỉ tạo tiếng ồn (5 mục đầu tiên của repo này đều thuộc loại đó).
        if not fm.get("plan", "").strip() and fm.get("area") not in ("flow", "infra"):
            same = plans_by_branch.get(fm.get("branch", "").strip(), [])
            if same:
                warns.append(f"{rel}: không gắn `plan:` mà nhánh "
                             f"{fm.get('branch')!r} đang mở plan {', '.join(same)} "
                             "— mục này sẽ không xuất hiện trong JOURNAL.md của plan")

        # Bốn field làm nên "bản tin quyết định" chứ không chỉ "ghi chép". Chúng
        # tuỳ chọn với mục cũ, nhưng đã khai thì phải khai đúng — sai giá trị thì
        # không lọc được, mà không lọc được thì cũng như không có.
        if fm.get("reversible") and fm["reversible"] not in {"yes", "costly", "no"}:
            errs.append(f"{rel}: reversible {fm['reversible']!r} không hợp lệ "
                        "(yes | costly | no)")
        if fm.get("deciders") and fm["deciders"] not in {"agent", "founder",
                                                         "agent+founder", "hook"}:
            errs.append(f"{rel}: deciders {fm['deciders']!r} không hợp lệ "
                        "(agent | founder | agent+founder | hook)")
        if fm.get("revisit") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fm["revisit"]):
            errs.append(f"{rel}: revisit {fm['revisit']!r} phải là ngày YYYY-MM-DD")
        # `kind: decision` mà không nói được quyết định là gì thì nó là ghi chép.
        if fm.get("kind") == "decision" and not fm.get("decision", "").strip():
            errs.append(f"{rel}: kind decision mà `decision:` rỗng — một câu khẳng "
                        "định nói rõ đã quyết cái gì")
        if fm.get("outcome") not in OUTCOMES:
            errs.append(f"{rel}: outcome không hợp lệ: {fm.get('outcome')!r}")

        for tid in ID_IN_LIST_RE.findall(fm.get("test_ids", "")):
            if tid not in CATALOG:
                errs.append(f"{rel}: test_ids trỏ ID không có trong catalog: {tid}")

        if fm.get("outcome") == "open":
            open_n += 1
        else:
            # "Đã nâng thành" là ô buộc trả lời câu "vậy lần sau thì sao".
            # Bỏ trống thì nhật ký chỉ còn là kể chuyện.
            if not fm.get("promoted_to"):
                errs.append(f"{rel}: đã đóng nhưng `promoted_to` trống — "
                            "trả lời bằng test ID / ADR / dòng skill, hoặc `none`")
            if "<điền khi đóng" in body:
                errs.append(f"{rel}: đã đóng nhưng thân còn chỗ trống chưa điền")

        n_body = len([l for l in body.splitlines() if l.strip()])
        if n_body > BODY_MAX:
            warns.append(f"{rel}: thân {n_body} dòng (trần {BODY_MAX}) — "
                         "dài thế này thì nó là ADR hoặc là test, không phải nhật ký")

        if n not in idx:
            errs.append(f"{rel}: chưa có trong INDEX.md — chạy `./mo steer index`")

    # supersedes phải trỏ tới mục có thật, nếu không chuỗi truy vết đứt.
    for sid, fm in entries.items():
        for ref in re.findall(r"S\d{4}", fm.get("supersedes", "")):
            if ref not in entries:
                errs.append(f".steering: {sid} supersedes {ref} — mục đó không tồn tại")

    if open_n:
        warns.append(f"{open_n} mục .steering/ còn `open` — đóng bằng "
                     "`./mo steer close <id> --outcome ... --why ... --promoted ...`")
    return errs, warns


def _fm_status(path):
    if not os.path.exists(path):
        return "?"
    t = open(path, encoding="utf-8").read()
    m = re.search(r"^status:\s*(\S+)", t, re.M)
    return m.group(1) if m else "?"


def _tracker_pass():
    """{ID: True/False} từ tracker — nguồn duy nhất để phán 'đã xong'."""
    import json
    p = os.path.join(ROOT, "docs", "test-status.json")
    if not os.path.exists(p):
        return {}
    return {k: v.get("status") == "pass"
            for k, v in json.load(open(p, encoding="utf-8"))["tests"].items()}


def check_plans(adr_st):
    """Plan trong .steering/plans/ phải nối đúng lên yêu cầu và xuống test ID.

    Ba mối nối, mỗi mối đứt một kiểu:
      covers → catalog   : ID ma thì tracker không bao giờ tick, hỏng im lặng
      adr    → docs/adr/ : plan dựa trên ADR đã supersede là plan đang làm theo
                           quyết định cũ mà không ai biết
      tasks  → covers    : task ngoài scope đã thoả thuận
    """
    errs, warns = [], []
    tests_pass = _tracker_pass()
    root = os.path.join(ROOT, PLANS_DIR)
    if not os.path.isdir(root):
        return errs, warns

    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if not os.path.isdir(d):
            continue
        rel = f"{PLANS_DIR}/{name}"

        missing = [f for f in ("spec.md", "clarify.md", "plan.md", "testcases.md", "tasks.md")
                   if not os.path.exists(os.path.join(d, f))]
        if missing:
            errs.append(f"{rel}: thiếu {', '.join(missing)} — bốn file là bắt buộc "
                        "(.steering/plans/TEMPLATE.md)")
        spec = os.path.join(d, "spec.md")
        if not os.path.exists(spec):
            continue

        fm = {}
        text = open(spec, encoding="utf-8").read()
        if text.startswith("---") and "\n---\n" in text:
            for line in text.split("\n---\n", 1)[0].lstrip("-\n").splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip()

        # `status` giờ là của TỪNG artifact: draft -> locked -> frozen (clarify: open/answered).
        # `abandoned` = bỏ giữa đường. Nó là một cửa ra HỢP LỆ: không có nó thì
        # cách duy nhất để bỏ một plan là xoá thư mục, và thư mục xoá không để
        # lại gì để truy vết.
        VALID = {"spec": {"draft", "locked", "frozen", "abandoned"},
                 "plan": {"draft", "locked", "frozen", "abandoned"},
                 "testcases": {"draft", "locked", "frozen", "abandoned"},
                 "tasks": {"draft", "locked", "frozen", "abandoned"},
                 "clarify": {"open", "answered", "frozen", "abandoned"}}
        for key, allowed in VALID.items():
            s = _fm_status(os.path.join(d, f"{key}.md"))
            if s != "?" and s not in allowed:
                errs.append(f"{rel}/{key}.md: status {s!r} không hợp lệ "
                            f"(cho phép: {', '.join(sorted(allowed))})")

        # Vòng đời plan: `supersedes` phải trỏ plan có thật, và plan đã đóng phải
        # nói được vì sao. Một plan `abandoned` không có lý do thì bằng đúng cái
        # nó thay thế — một thư mục bị xoá.
        for old in re.findall(r"[\w.-]+", fm.get("supersedes", "")):
            if not os.path.isdir(os.path.join(root, old)):
                errs.append(f"{rel}/spec.md: supersedes trỏ plan không tồn tại: {old} "
                            "— plan cũ phải còn nguyên trong .steering/plans/, "
                            "đừng xoá (dùng `./mo steer plan abandon`)")
        # `contract:` — file hợp đồng plan sẽ chạm. Khai sai đường dẫn thì chốt
        # chặn contract_touch.py sẽ cho qua một file lẽ ra phải chặn, hoặc chặn
        # một file lẽ ra được phép: cả hai đều là chốt chặn nói dối.
        for c in re.split(r"[,\s]+", fm.get("contract", "").strip("[]")):
            if not c:
                continue
            if not c.startswith("specs/"):
                errs.append(f"{rel}/spec.md: contract chỉ nhận đường dẫn trong "
                            f"specs/ — không hợp lệ: {c}")
            elif c.endswith("/"):
                if not os.path.isdir(os.path.join(ROOT, c)):
                    errs.append(f"{rel}/spec.md: contract trỏ thư mục không tồn tại: {c}")
            elif not os.path.exists(os.path.join(ROOT, c)):
                warns.append(f"{rel}/spec.md: contract trỏ {c} chưa tồn tại "
                             "— plan sẽ tạo?")

        closed_as = fm.get("closed_as", "").strip()
        if closed_as and closed_as not in ("frozen", "abandoned"):
            errs.append(f"{rel}/spec.md: closed_as {closed_as!r} không hợp lệ "
                        "(frozen | abandoned)")
        if fm.get("closed", "").strip() and not fm.get("why_closed", "").strip('" '):
            errs.append(f"{rel}/spec.md: đã đóng ({closed_as or '?'}) mà `why_closed:` "
                        "rỗng — người sau chỉ còn ô này để hiểu vì sao dừng")
        if closed_as and not fm.get("closed", "").strip():
            errs.append(f"{rel}/spec.md: có closed_as mà thiếu mốc `closed:`")

        covers = set(ID_IN_LIST_RE.findall(fm.get("covers", "")))
        if not covers:
            errs.append(f"{rel}/spec.md: `covers:` rỗng — feature không cover test ID nào "
                        "là feature không hợp lệ")
        for tid in covers:
            if tid not in CATALOG:
                errs.append(f"{rel}/spec.md: covers trỏ ID không có trong catalog: {tid}")

        for num in re.findall(r"\d{4}", fm.get("adr", "")):
            if num not in adr_st:
                errs.append(f"{rel}/spec.md: adr trỏ tới ADR-{num} không tồn tại")
            elif adr_st[num] == "superseded":
                errs.append(f"{rel}/spec.md: dựa trên ADR-{num} đã superseded — "
                            "cập nhật plan hoặc viết plan mới")

        tasks = os.path.join(d, "tasks.md")
        if os.path.exists(tasks) and covers:
            body = open(tasks, encoding="utf-8").read()
            body = body.split("\n---\n", 1)[-1]
            extra = set(ID_IN_LIST_RE.findall(body)) - covers
            if extra:
                warns.append(f"{rel}/tasks.md: có ID ngoài `covers:` của spec.md: "
                             f"{', '.join(sorted(extra))} — hoặc mở rộng covers, hoặc bỏ task")

            # Chống tick tay. Dấu tích trong tasks.md phải suy được từ tracker;
            # nếu không, nó thành nguồn "đã xong" thứ hai và sẽ mâu thuẫn với
            # docs/test-status.md — đúng thứ constitution #2 chặn.
            for line in body.splitlines():
                m = re.match(r"^\s*-\s*\[([xX])\](\s+.*)$", line)
                if not m:
                    continue
                ids = ID_IN_LIST_RE.findall(m.group(2))
                red = [i for i in ids if tests_pass.get(i) is not True]
                if not ids:
                    errs.append(f"{rel}/tasks.md: task tick [x] mà không có test ID: "
                                f"{line.strip()[:60]}")
                elif red:
                    errs.append(f"{rel}/tasks.md: task tick [x] nhưng {', '.join(red)} "
                                "chưa xanh trong tracker — dấu tích chỉ do "
                                "`./mo steer plan sync` điền, không tick tay")

        # Cổng chốt tuần tự: không thể chốt cái sau khi cái trước còn draft.
        order = ["spec", "plan", "testcases", "tasks"]
        st = {k: _fm_status(os.path.join(d, f"{k}.md")) for k in order}
        for i in range(1, len(order)):
            if st[order[i]] == "locked" and st[order[i - 1]] == "draft":
                errs.append(f"{rel}: {order[i]}.md đã chốt nhưng {order[i-1]}.md còn draft "
                            "— gate tuần tự bị lách, chốt lại theo thứ tự")

        tc = os.path.join(d, "testcases.md")
        if os.path.exists(tc) and covers:
            heads = set(ID_IN_LIST_RE.findall(" ".join(
                l for l in open(tc, encoding="utf-8").read().splitlines()
                if l.startswith("## "))))
            miss = sorted(covers - heads)
            if miss and st.get("testcases") == "locked":
                errs.append(f"{rel}/testcases.md: đã chốt nhưng thiếu thiết kế test cho "
                            f"{', '.join(miss)}")
            elif miss:
                warns.append(f"{rel}/testcases.md: chưa có mục `## <ID>` cho {', '.join(miss)}")
    return errs, warns


def check_milestones():
    """MILESTONE trong track.py phải khớp tiêu đề nhóm trong 05-test-catalog.md.

    Catalog là thứ người đọc và sửa; MILESTONE là thứ máy dùng để tính "việc tiếp
    theo". Hai chỗ nói khác nhau thì tracker sẽ chỉ sai việc — im lặng và tin được,
    kiểu sai tệ nhất. Nối chúng bằng chữ cái nhóm (A, B, C...).
    """
    errs = []
    path = os.path.join(ROOT, CATALOG_MD)
    if not os.path.exists(path):
        return [f"không tìm thấy {CATALOG_MD} để đối chiếu milestone"]

    md = open(path, encoding="utf-8").read()

    # CATALOG (track.py) phải khớp bảng trong catalog.md, cả hai chiều.
    # Quy tắc catalog #3 buộc sửa hai chỗ CÙNG một commit; quên một bên thì
    # track.py bỏ qua ID đó im lặng — test xanh mà không bao giờ được tick.
    in_md = set(re.findall(r"^\|\s*([A-Z]{3}-\d{2})\s*\|", md, re.M))
    only_md = sorted(in_md - set(CATALOG))
    only_py = sorted(set(CATALOG) - in_md)
    if only_md:
        errs.append(f"{CATALOG_MD} có ID mà CATALOG của track.py thiếu: {', '.join(only_md)} "
                    "— tracker sẽ bỏ qua chúng")
    if only_py:
        errs.append(f"track.py có ID mà {CATALOG_MD} thiếu: {', '.join(only_py)}")

    # "## A. Provisioning & danh tính (M1)" / "## I. Tải & bền bỉ (M6 — hardening)"
    head_re = re.compile(r"^##\s+([A-Z])\.\s+[^(\n]*\((M\d(?:–M\d)?)", re.M)
    from_md = {m.group(1): m.group(2) for m in head_re.finditer(md)}

    for gname, prefix in GROUPS:
        letter = gname.split(" ")[0]              # "A · Provisioning" -> "A"
        prefixes = prefix if isinstance(prefix, tuple) else (prefix,)
        if letter not in from_md:
            errs.append(f"catalog thiếu tiêu đề nhóm {letter} có ghi milestone dạng (M1)")
            continue
        for p in prefixes:
            if MILESTONE.get(p) != from_md[letter]:
                errs.append(
                    f"milestone lệch cho nhóm {letter} ({p}): track.py ghi "
                    f"{MILESTONE.get(p)!r}, {CATALOG_MD} ghi {from_md[letter]!r}"
                )
    return errs


# File được GỌI THẲNG (không qua `bash x.sh`), nên bit thực thi phải nằm trong git.
# Dev trên Windows có core.fileMode=false: chmod tại máy không vào index, nên
# runner Linux và mọi bản clone khác nhận file 644. `./mo` -> "Permission denied";
# git hook thì không chạy và KHÔNG báo gì cả — chốt chặn biến mất im lặng.
MUST_EXEC = ["mo", ".githooks/commit-msg", ".githooks/post-merge",
             ".githooks/post-checkout", ".claude/statusline.sh"]


def check_exec_bits():
    errs = []
    out = subprocess.run(["git", "ls-files", "-s"] + MUST_EXEC,
                         capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:
        return errs
    seen = set()
    for line in out.stdout.splitlines():
        parts = line.split(maxsplit=3)
        if len(parts) < 4:
            continue
        mode, path = parts[0], parts[3]
        seen.add(path)
        if mode != "100755":
            errs.append(f"{path}: mode {mode} trong git, phải là 100755 — "
                        f"sửa: git update-index --chmod=+x {path}")
    for p in MUST_EXEC:
        if p not in seen and os.path.exists(os.path.join(ROOT, p)):
            errs.append(f"{p}: có trên đĩa nhưng chưa được git theo dõi")
    return errs


def main():
    errors, warns = [], []
    statuses = adr_status()

    errors += check_exec_bits()
    errors += check_milestones()
    errors += check_frontmatter()
    steer_errs, steer_warns = check_steering()
    errors += steer_errs
    warns += steer_warns
    plan_errs, plan_warns = check_plans(statuses)
    errors += plan_errs
    warns += plan_warns

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

    # Tracker xanh mà test biến mất = tracker đang nói dối, im lặng.
    # track.py chỉ cập nhật những ID CÓ MẶT trong output `go test`, nên xoá hoặc đổi
    # tên một test đã xanh thì ô đó giữ ✅ vĩnh viễn. track.py không tự thấy được
    # (nó chỉ có output), còn chỗ này đọc được mã nguồn — nên chốt chặn thuộc về đây.
    # LỖI chứ không phải cảnh báo: "chưa có test" là bình thường ở M0, còn "đã tick
    # rồi mà test biến mất" thì không có ngữ cảnh nào biện minh được.
    # Test [H] không có test Go — người tick bằng biên bản `./mo hw-test` — nên loại ra.
    for tid, ok in sorted(_tracker_pass().items()):
        if not ok or tid not in CATALOG or CATALOG[tid][0] == "H" or tid in test_ids:
            continue
        errors.append(
            f"{tid} đang ✅ trong tracker nhưng không còn test Go nào mang ID này — "
            f"test bị xoá hoặc đổi tên sau khi tick. Khôi phục test (đúng tên "
            f"Test{tid.replace('-', '')}_...); nếu ID này thật sự bỏ thì gỡ khỏi "
            f"{CATALOG_MD} và CATALOG của track.py trong cùng một commit.")

    # skill <-> ADR  (statuses đã lấy ở đầu main, dùng chung với check_plans)
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
