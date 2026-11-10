# 09 — Kế hoạch tách repo

Quyết định: ADR-0019. File này là bản chạy từng bước. Nó trả lời bốn câu: **ai làm gì, theo thứ tự nào, bằng lệnh nào, và xong khi nào.**

File này chỉ nói chuyện tổ chức repo. Công nghệ của từng repo (ngôn ngữ, thư viện, cách sinh mã) do ADR của repo đó quyết, không bàn ở đây.

Trong file, `<org>` là tên GitHub Organization, founder chọn ở mục 10.

## 0. Trạng thái thực hiện (cập nhật 2026-11-09)

Founder yêu cầu tách ngay, trước khi xong T0–T3. Đã làm theo cách thực dụng: mỗi repo đội mang bộ công cụ hiện có, chỉ sửa tối thiểu để `./mo verify` và `./mo trace` xanh. Phần T3 (công cụ đọc `mechops.repo.toml`, gom `--all`, chốt chặn ADR bất biến) vẫn còn phải làm.

| Việc | Trạng thái |
|---|---|
| Ba repo trên GitHub | đã tạo **dưới tài khoản `NguyenVu1010`**, chưa có Organization; chuyển vào Organization sau bằng `transfer` |
| `mechops-agent` | `develop`, tag `v0.0.1`, `spec-v0.1.0`; lịch sử từ `filter-repo`; có `sim/ros2/`, LICENSE Apache 2.0; gitleaks sạch (26 commit); **vẫn private**, founder chuyển public |
| `mechops-platform` | `develop`, tag `v0.0.1`, `api-v0.0.1`; `specs/` ghim `spec-v0.1.0`; lệnh `./mo spec-sync <tag>` chạy được với repo thật |
| `mechops-mobile` | `develop`, tag `v0.0.1`; `api/` ghim `api-v0.0.1`; lệnh `./mo api-sync <tag>`; nháp `MOB-0001` |
| `mechops-robotics-backend` | tạo 2026-11-10 theo quyết định của founder (ADR-0019 chuẩn hoá, ADR-0020); `develop`, tag `v0.0.1`; `pinned/specs/` ghim `spec-v0.1.0`, `pinned/platform-api/` ghim `api-v0.0.1`; `api/` chờ `coord.yaml`; nháp `RBE-0001` |
| Bản sao ADR | **mỗi repo đội giữ bản sao ADR liên quan**: agent 14, platform 16, mobile 12, robotics-backend 13 (tính cả ADR-0020). Kế hoạch cũ chỉ cho agent giữ, nhưng `trace` và skill cần đọc ADR ngay trong repo |
| Repo chính thành umbrella (T6) | PR riêng, xếp sau PR này |
| Bảo vệ nhánh ở ba repo mới | **chưa có**: GitHub từ chối ruleset trên repo private của gói miễn phí. Cần GitHub Pro, gói Team của Organization, hoặc repo public |
| T2 (cột Repo trong catalog) | chưa làm; tạm thời mỗi repo khai `owned_tests` trong `mechops.repo.toml` |
| T3 (bộ công cụ biết vai trò repo) | chưa làm |
| Image dev của platform lên GHCR, compose kéo image ở mobile | chưa làm |
| Workflow nightly | bỏ ở agent và mobile (nó dựng hạ tầng từ `deploy/` của platform) |
| T7 (PR thử từng đội) | chưa làm |

**Phát hiện cần founder quyết:** repo `MechOps` hiện đang **public**. Mã server và dashboard, phần đóng theo ADR-0002, đã công khai trong lịch sử. Kế hoạch ghi repo chính là private. Nhưng nếu chuyển sang private trên gói miễn phí thì ruleset của `develop` sẽ mất hiệu lực.

## 1. Kết quả cuối

```
<org>/mechops                    repo chính (umbrella), private — chính là repo hiện tại
├── constitution.md              bản gốc duy nhất
├── docs/adr/                    ADR-0001..0019 và ADR toàn hệ mới (ADR-0020 trở đi)
├── docs/product/                spec sản phẩm, master plan, catalog gom (máy sinh)
├── .steering/                   toàn bộ lịch sử trước khi tách + INDEX/HISTORY gom (máy sinh)
├── e2e/                         test E2E, compose ghép bản release của các repo đội
└── repos/
    ├── platform/  → submodule <org>/mechops-platform @ tag   (đội web)
    ├── agent/     → submodule <org>/mechops-agent    @ tag   (đội robotics, public)
    ├── mobile/    → submodule <org>/mechops-mobile   @ tag   (đội mobile)
    └── robotics-backend/ → submodule <org>/mechops-robotics-backend @ tag (đội robotics-backend)
```

Ba quy tắc vận hành:

- **Mỗi đội chỉ clone repo của mình.** Repo chính dành cho founder, CI tích hợp và Claude.
- **Submodule chỉ trỏ vào tag**, đổi tag qua PR, PR chỉ merge khi `e2e/` xanh.
- **Clone repo chính bằng `--recurse-submodules` rồi chạy `./mo status --all`** là thấy ADR, nhật ký và tracker của mọi repo ở một chỗ.

Submodule nằm dưới `repos/` để không trùng tên với thư mục cũ. Ví dụ: repo agent có thư mục `agent/` bên trong, nên nếu submodule cũng tên `agent/` thì đường dẫn thành `agent/agent/`.

## 2. Lịch và người làm

Lịch dự kiến cho team part-time. Bước nào cũng chỉ bắt đầu khi bước trước đã nghiệm thu.

| Bước | Việc | Người | Thời lượng | Dự kiến |
|---|---|---|---|---|
| T0 | Chốt và dọn trong repo hiện tại | founder | 2–3 ngày | 2026-11-09 → 11-11 |
| T1 | GitHub Organization, team, repo rỗng | founder | 1 ngày | 2026-11-12 |
| T2 | Sổ sách: catalog, plan, CODEOWNERS nháp | founder | 2 ngày | 2026-11-13 → 11-14 |
| T3 | Bộ công cụ chạy được ở nhiều repo | founder | 4–5 ngày | 2026-11-16 → 11-20 |
| T4 | Rút repo platform và agent | founder | 1–2 ngày | 2026-11-23 → 11-24 |
| T5 | Khung repo mobile | founder | 1 ngày | 2026-11-25 |
| T6 | Biến repo hiện tại thành umbrella | founder | 2 ngày | 2026-11-26 → 11-27 |
| T7 | Nghiệm thu tổng, bàn giao cho ba đội | ba đội, founder | 1 ngày | 2026-11-30 |

M0' (`08-master-plan.md`) mở lại từ 2026-12-01 trong các repo đội.

## 3. Bản đồ di chuyển

### 3.1 Thứ hiện có đi về đâu

| Hiện tại | Về | Ghi chú |
|---|---|---|
| `agent/`, `probe/`, `sim/`, `specs/`, `docs/protocol-notes.md` | agent | `sim/` phải vào git ở T0 |
| `server/`, `protocol/`, `dashboard/`, `deploy/` | platform | `protocol/` thành mã sinh từ `specs/` |
| `go.work`, `.golangci.yml`, `.golangci-version` | platform | `go.work` bỏ dòng `./agent` |
| `mo`, `mo.ps1`, `Makefile`, `tools/`, `.githooks/`, `.gitattributes`, `.gitignore`, `docker/`, `docker-compose.dev.yml` | cả bốn repo | mỗi repo giữ lịch sử, rồi tỉa phần không dùng |
| `.claude/` | cả bốn repo | xem mục 3.3 |
| `.github/` | cả bốn repo | mỗi repo viết lại CI của mình |
| `constitution.md` | repo chính | repo đội giữ bản sao chỉ-đọc, CI kiểm khớp |
| `docs/adr/` | repo chính | mỗi repo đội giữ bản sao ADR liên quan: agent 14, platform 16, mobile 12 |
| `docs/product/`, `docs/evidence/`, `docs/hw-test-runs/` | repo chính | biên bản [H] mới nằm ở repo sở hữu ID đó |
| `.steering/` | repo chính | lịch sử ở lại nguyên vẹn; repo đội bắt đầu `.steering/` rỗng |
| `docs/test-status.*`, `docs/PROGRESS.md`, `docs/module-status.json` | mỗi repo tự sinh | repo chính gom bằng `--all` |
| `CLAUDE.md`, `README.md`, `REVIEW.md`, `docs/DEVELOPMENT.md` | mỗi repo tự viết | |

### 3.2 Danh sách đường dẫn cho `git filter-repo`

Phần dùng chung, cả hai repo cùng giữ để không mất lịch sử của bộ công cụ:

```
--path mo --path mo.ps1 --path Makefile --path tools/ --path .githooks/
--path .gitattributes --path .gitignore --path docker/ --path docker-compose.dev.yml
--path .claude/ --path .github/ --path constitution.md
```

Riêng `mechops-agent`:

```
--path agent/ --path probe/ --path sim/ --path specs/ --path docs/protocol-notes.md
--path docs/adr/0001-mqtt-over-custom-tcp.md
--path docs/adr/0002-open-core-apache2-agent.md
--path docs/adr/0004-probe-api-unix-socket.md
--path docs/adr/0005-ota-rollback-at-agent.md
--path docs/adr/0008-tenant-in-topic-from-day-one.md
--path docs/adr/0010-toolchain-trong-docker.md
--path docs/adr/0011-cuong-che-trong-ci-khong-trong-van-ban.md
--path docs/adr/0012-rust-cho-agent.md
--path docs/adr/0013-probe-cpp-rclcpp.md
--path docs/adr/0015-ota-tu-xay-khong-wrap-mender.md
--path docs/adr/0016-pki-ca-trong-server.md
--path docs/adr/0018-moi-truong-mo-phong-ros2-wsl-container.md
--path docs/adr/0019-tach-repo-theo-doi-umbrella-submodule.md
```

Riêng `mechops-platform`:

```
--path server/ --path protocol/ --path dashboard/ --path deploy/
--path go.work --path .golangci.yml --path .golangci-version
```

Không giữ bằng `filter-repo`, vì repo chính giữ bản gốc: `docs/product/`, `.steering/`, `docs/test-status.*`, `docs/PROGRESS.md`, `docs/evidence/`, `docs/hw-test-runs/`, `CLAUDE.md`, `README.md`, `REVIEW.md`, `docs/DEVELOPMENT.md`.

### 3.3 `.claude/` của từng repo

| Repo | Skill giữ | Bỏ |
|---|---|---|
| repo chính | `adr`, `brainstorm`, `steering`, `feature`, `feature-spec`, `spec-analyze`, `handoff`, `dev`, `pr` | skill theo ngôn ngữ |
| platform | `go-conventions`, `task`, `tech-plan`, `audit`, `bug-to-test`, `troubleshoot`, `test-evidence`, `security-guard`, `contract-guard`, `pr`, `dev`, `handoff` | `rust-conventions`, rule `agent-ota` |
| agent | `rust-conventions`, `task`, `tech-plan`, `audit`, `bug-to-test`, `troubleshoot`, `test-evidence`, `security-guard`, `contract-guard`, `pr`, `dev`, `handoff` | `go-conventions`, rule `server-data` |
| mobile | `task`, `audit`, `bug-to-test`, `troubleshoot`, `pr`, `dev`, `handoff` | skill theo ngôn ngữ, cả hai rule |

Agent `spec-guardian` và `test-auditor` có ở cả ba repo đội.

## 4. Chia 49 test ID

Luật: một ID thuộc về repo nơi bài test của nó chạy được mà không cần repo khác (ADR-0019).

| Repo | ID | Số |
|---|---|---|
| agent | PRB-01..06 · TEL-01, TEL-02, TEL-05, TEL-06, TEL-07 · ACL-04 · OTA-01..08, OTA-10..12 | 23 |
| platform | ACL-01..03 · OTA-09 · ALT-01..04 · TRM-02 · WLB-01 · INS-01..03 | 13 |
| E2E (repo chính) | PRV-01..05 · TEL-03, TEL-04 · TRM-01, TRM-03, TRM-04 · LOD-01..03 | 13 |

Ghi chú về cách chia:

- **TEL-01** thuộc agent vì agent giữ test vector. Platform chạy cùng bộ vector khi kiểm `spec sync`, nhưng không tick ID này.
- **ACL-04** thuộc agent, theo bảng M1 của master plan: giới hạn 64 KB là việc của agent.
- **OTA-09** là rollout theo wave của Fleet Manager, nên thuộc platform. Các ID OTA khác chỉ cần agent, registry và một lệnh giả.
- **PRV** và **TEL-03, TEL-04** chỉ quan sát được khi agent thật và server thật cùng chạy, nên là E2E.
- Mobile chưa có ID. Đội mobile tạo nhóm `MOB-xx` khi bắt đầu việc.

Sau khi tách, mỗi repo đội giữ catalog phần của mình ở `docs/test-catalog.md`. Repo chính giữ phần E2E ở `e2e/test-catalog.md`. File `docs/product/05-test-catalog.md` của repo chính trở thành bản gom do máy sinh.

## 5. ADR sau khi tách

- **19 ADR hiện có nằm nguyên ở repo chính**, không đổi số. Chúng bất biến từ tag `pre-split`.
- **Mỗi repo đội giữ bản sao chỉ-đọc của ADR liên quan**: ADR toàn hệ (0001, 0002, 0005, 0008, 0010, 0011, 0015, 0016, 0019, 0020) cộng ADR của đội. Agent thêm 0004, 0012, 0013, 0018 (14 bản). Platform thêm 0003, 0006, 0007, 0009, 0014, 0017 (16 bản). Mobile thêm 0007, 0017 (12 bản). Sáu ADR chỉ thuộc web không ra repo public. Robotics-backend giữ bản sao ADR toàn hệ cộng 0003, 0014 (broker) và 0013 (probe) (13 bản). ADR riêng của đội này đánh số `RBE-`.
- **ADR mới chạm từ hai repo trở lên** viết ở repo chính, đánh số từ `ADR-0020`.
- **ADR của riêng một đội** viết ở repo của đội đó, đánh số `WEB-0001`, `ROB-0001`, `MOB-0001`.

## 6. Các bước chi tiết

### T0 — Chốt và dọn trong repo hiện tại

**Mục tiêu:** repo hiện tại ở trạng thái sạch, đóng băng được, có điểm quay về.

**Đầu vào:** nhánh `docs/adr-0019-repo-split` (ADR-0019, đợt chuẩn hoá ADR, file này).

**Việc:**

1. Mở PR từ nhánh `docs/adr-0019-repo-split` vào `develop`. Founder duyệt và merge.
2. Founder trả lời bốn câu hỏi ở mục 10.
3. Đưa `sim/ros2/` vào git bằng một PR riêng. Với bộ đo module, làm theo câu trả lời số 3 của founder: đưa vào git trong cùng PR đó, hoặc xoá khỏi máy.
4. Trả lời triage cho plan `m1-contract-v01`:
   ```bash
   ./mo steer plan abandon m1-contract-v01 --why "..." --next "mechops-agent:<plan mới>"
   # hoặc
   ./mo steer plan keep m1-contract-v01 --why "..."
   ```
   Thư mục plan không được xoá và không được chuyển đi, vì luật cấm xoá thư mục trong `.steering/plans/`. Nếu việc đó còn làm tiếp, plan mới mở trong repo agent sau T4, và plan cũ ở repo chính được `abandon` với `--next` trỏ tới plan mới.
5. **Gỡ dòng ghi công AI khỏi lịch sử cũ: đã làm ngày 2026-11-08.** `develop`, `main` và `feat/ai-flow` được viết lại bằng `filter-repo`, chỉ bỏ dòng `Co-Authored-By: Claude…` và `Claude-Session:`. Cây file, tác giả và ngày của mọi commit giữ nguyên. Nhánh đã merge `docs/adr-0012-0018-master-plan` đã xoá. `feat/ai-flow` được giữ lại vì còn hai commit chưa vào `develop`. Bản sao lưu trước khi viết lại: `C:\Users\NguyenVD\wsl-backup\mechops-before-rewrite-20261108.bundle`. Nhật ký: S0016–S0019.
6. Kiểm không còn PR mở, rồi đánh tag:
   ```bash
   gh pr list --state open            # phải rỗng
   git fetch origin
   git tag -a pre-split origin/develop -m "Điểm quay về trước khi tách repo (ADR-0019)"
   git push origin pre-split
   ```

**Đầu ra:** `develop` sạch, có tag `pre-split`. Cửa sửa ADR đóng từ đây.

**Nghiệm thu:**
```bash
./mo trace                     # OK
./mo steer plan triage         # rỗng
gh pr list --state open        # rỗng
git ls-remote --tags origin pre-split   # có
```

**Quay lui:** chưa có gì thay đổi bên ngoài repo hiện tại.

### T1 — Tổ chức GitHub

**Mục tiêu:** có chỗ cho ba team và bốn repo, quyền đúng ngay từ đầu.

**Việc (founder):**

1. Tạo Organization `<org>` trên web GitHub. `gh` không tạo được Organization.
2. Chuyển repo hiện tại vào Organization. GitHub giữ redirect cho URL cũ, nên remote cũ vẫn chạy.
   ```bash
   gh api -X POST repos/NguyenVu1010/MechOps/transfer -f new_owner=<org> -f new_name=mechops
   git remote set-url origin git@github.com:<org>/mechops.git
   ```
3. Tạo ba team và ba repo rỗng:
   ```bash
   for t in web robotics mobile; do gh api -X POST orgs/<org>/teams -f name=$t -f privacy=closed; done
   for r in mechops-platform mechops-agent mechops-mobile; do gh repo create <org>/$r --private; done
   ```
4. Gán quyền: team `web` được `write` trên platform, team `robotics` được `write` trên agent, team `mobile` được `write` trên mobile. Cả ba team được `read` trên repo chính.
5. Chưa bật branch protection ở bước này, vì repo rỗng chưa có nhánh `develop`. Bật ở T4 và T5.

**Nghiệm thu:** có ba team và bốn repo. Một thành viên team mobile không push được vào repo platform.

**Quay lui:** chuyển repo về tài khoản cá nhân bằng cùng lệnh `transfer`.

### T2 — Sổ sách, trong repo hiện tại

**Mục tiêu:** mọi thứ cần chia đã được gắn nhãn repo trước khi chia, để T4 chỉ là việc cơ học.

**Việc (một PR):**

1. `05-test-catalog.md` thêm cột "Repo", điền theo mục 4. `track.py` đọc cột này.
2. Mỗi plan trong `.steering/plans/` thêm trường `repo:` trong frontmatter.
3. Viết CODEOWNERS cho bốn repo theo mục 7.3, dưới dạng file nháp trong `docs/product/codeowners/`.
4. Viết `mechops.repo.toml` cho bốn repo theo mục 7.1, cũng dạng nháp trong `docs/product/codeowners/`.
5. Thêm chốt chặn trong `./mo trace`: báo lỗi nếu có ID không có repo, hoặc có ID thuộc hai repo.

**Nghiệm thu:**
```bash
./mo verify && ./mo trace      # xanh
# đổi tạm một ô Repo thành rỗng → ./mo trace phải đỏ, rồi trả lại
```

**Quay lui:** revert PR.

### T3 — Bộ công cụ chạy được ở nhiều repo

**Mục tiêu:** `./mo` và `tools/` chạy đúng ở cả bốn vai trò, trước khi có repo thật nào. Đây là bước lớn nhất, và nằm trong ngoại lệ đóng băng `tools/` của ADR-0019.

**Việc (một PR):**

1. `tools/` đọc `mechops.repo.toml` ở gốc repo. Thiếu file này thì repo được coi là repo cũ (monorepo), để repo hiện tại vẫn chạy trong lúc làm.
2. `trace.py`:
   - Đọc tiền tố ADR từ cấu hình: repo chính dùng số trần, repo đội dùng `WEB-`, `ROB-`, `MOB-`.
   - Ở repo chính, kiểm qua submodule: ADR của repo đội không lật ADR của repo chính; bản sao ADR và constitution khớp bản gốc; không ID nào trùng giữa các repo.
   - Ở mọi repo, chặn PR sửa nội dung một ADR đã accepted. Chỉ dòng Status được đổi, và chỉ khi cùng PR có ADR mới supersede nó.
3. Ở repo chính, `steer.py index --all` và `track.py --all` đọc `.steering`, catalog và tracker của từng submodule, rồi sinh INDEX, HISTORY, catalog gom và test-status gom.
4. Thêm lệnh `./mo spec sync <tag>` cho platform và `./mo api sync <tag>` cho mobile. Lệnh tải đúng tag, chạy bước sinh mã, ghi tag vào một file phiên bản, và CI kiểm mã sinh khớp tag. Cách sinh mã cụ thể là việc của ADR từng repo. Ở T3 chỉ cần lệnh chạy được với một tag thử.
5. Chia `docker/dev.Dockerfile` theo vai trò. Repo chính chỉ cần Python và git, cộng `git-filter-repo` cho T4.
6. Chạy thử toàn bộ việc tách trên bản sao local:
   ```bash
   git clone --no-local . ../dry-agent    && (cd ../dry-agent    && git filter-repo <đường dẫn mục 3.2, phần chung + agent>)
   git clone --no-local . ../dry-platform && (cd ../dry-platform && git filter-repo <đường dẫn mục 3.2, phần chung + platform>)
   # đặt mechops.repo.toml nháp vào mỗi bản, rồi
   (cd ../dry-agent && ./mo verify && ./mo trace)
   (cd ../dry-platform && ./mo verify && ./mo trace)
   ```

**Nghiệm thu:**
- Test của chính `tools/` xanh.
- Hai bản chạy thử xanh `verify` và `trace`.
- `./mo status --all` trên một umbrella chạy thử gom đủ 49 ID, mỗi ID đúng một repo.
- Một PR thử sửa nội dung một ADR cũ bị `trace` chặn.

**Quay lui:** nếu T3 quá 5 ngày mà chưa xong, dừng tách. Giữ monorepo, chia quyền bằng CODEOWNERS (phương án 1 của ADR-0019), và viết ADR mới ghi lý do. Không âm thầm bỏ dở.

### T4 — Rút platform và agent

**Mục tiêu:** hai repo đội có lịch sử, CI xanh, tag đầu tiên. Repo agent chuyển public.

**Việc:**

1. Rút repo agent:
   ```bash
   git clone --no-local --branch develop git@github.com:<org>/mechops.git split-agent
   cd split-agent
   git filter-repo <đường dẫn mục 3.2, phần chung + agent> --message-callback '
   import re
   return re.sub(rb"\n(?i:co-authored-by:[^\n]*(?:claude|anthropic)[^\n]*|claude-session:[^\n]*)", b"", message)'
   ```
   Lịch sử đã sạch từ 2026-11-08, nên callback này chỉ là lớp chặn thêm, phòng khi có commit mang dòng ghi công lọt vào trước khi tách.
2. Dọn trong `split-agent`, bằng một commit thường:
   - Thêm `mechops.repo.toml` và CODEOWNERS từ bản nháp T2.
   - Tỉa `.claude/` theo mục 3.3.
   - Thêm toàn văn license Apache 2.0, `README.md`, `CLAUDE.md` riêng, catalog phần agent, và `.steering/` rỗng có README và TEMPLATE.
   - Thêm file compose chạy broker trần với ACL mẫu, đủ để test ID của agent chạy mà không cần server.
3. Quét bí mật trên toàn bộ lịch sử. Bước này phải xong trước khi push lên GitHub:
   ```bash
   docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:v8.18.4 detect --source /repo --log-opts="--all"
   ```
   Có phát hiện thì dừng, dọn bằng `filter-repo`, rồi quét lại.
4. Push lên repo agent, đánh tag đầu tiên, và bật branch protection theo mục 7.4:
   ```bash
   git remote add origin git@github.com:<org>/mechops-agent.git
   git push -u origin develop
   git tag -a v0.0.1 -m "Bản đầu sau khi tách" && git tag -a spec-v0.1.0 -m "Hợp đồng đầu tiên"
   git push origin v0.0.1 spec-v0.1.0
   ```
5. Làm tương tự cho platform, với đường dẫn phần chung cộng platform và cùng `--message-callback`. Thêm:
   - `mechops.repo.toml`, CODEOWNERS, `.claude/` đã tỉa.
   - Catalog phần platform.
   - Job phát hành image dev lên GHCR mỗi lần merge, image kèm user seed.
   - Tag đầu tiên `v0.0.1` và `api-v0.0.1`.
6. Platform chạy `./mo spec sync spec-v0.1.0` lần đầu, rồi commit mã sinh.
7. Founder chuyển repo agent sang public. Bước này không rút lại được:
   ```bash
   gh repo edit <org>/mechops-agent --visibility public --accept-visibility-change-consequences
   ```

**Đầu ra:** hai repo có `develop`, có tag, có CI riêng. Repo chính chưa đổi gì.

**Nghiệm thu:**
- CI của cả hai repo xanh `verify` và `trace`.
- Trong platform, CI kiểm được mã sinh khớp `spec-v0.1.0`.
- `gitleaks` không phát hiện gì.
- Push thẳng vào `develop` của cả hai repo bị từ chối.
- Repo agent public.

**Quay lui:** xoá hai repo mới. Trước khi agent public, việc này không để lại dấu vết gì. Repo chính vẫn còn nguyên mọi thứ.

### T5 — Repo mobile

**Mục tiêu:** đội mobile có repo chạy được, biết rõ hợp đồng mình dùng.

**Việc:**

1. Dựng khung: `mechops.repo.toml`, `./mo`, `.claude/` đã tỉa, CI, catalog rỗng, `.steering/` rỗng, bản sao constitution, CODEOWNERS.
2. Viết `MOB-0001` dạng nháp: phần context và các phương án cho stack. Đội mobile tự viết phần quyết định.
3. Thêm lệnh `./mo api sync api-v0.0.1`. Lệnh phải chạy được dù client sinh ra còn rỗng.
4. Thêm file compose kéo image dev của platform từ GHCR.
5. Push lên repo mobile, đánh tag `v0.0.1`, bật branch protection.

**Nghiệm thu:**
- `./mo verify` xanh với 0 test, `./mo trace` xanh.
- `docker compose up` trong repo mobile kéo được image platform, và đăng nhập được bằng user seed.

**Quay lui:** xoá repo mobile.

### T6 — Biến repo hiện tại thành umbrella

**Mục tiêu:** repo hiện tại chỉ còn vai trò umbrella, ghim ba repo đội theo tag.

**Việc (một PR):**

1. Xoá các thư mục đã chuyển đi bằng commit thường, không viết lại lịch sử:
   ```bash
   git rm -r agent probe sim specs docs/protocol-notes.md server protocol dashboard deploy \
             go.work .golangci.yml .golangci-version
   ```
2. Thêm submodule, ghim vào tag:
   ```bash
   git submodule add git@github.com:<org>/mechops-platform.git repos/platform
   git submodule add git@github.com:<org>/mechops-agent.git    repos/agent
   git submodule add git@github.com:<org>/mechops-mobile.git   repos/mobile
   (cd repos/platform && git checkout v0.0.1)
   (cd repos/agent    && git checkout v0.0.1)
   (cd repos/mobile   && git checkout v0.0.1)
   git add .gitmodules repos
   ```
3. Thêm `mechops.repo.toml` vai trò `umbrella`, và tỉa `.claude/` theo mục 3.3.
4. Dựng khung `e2e/`: catalog phần E2E, và file compose ghép image platform với binary agent lấy từ release của tag đang ghim.
5. CI của repo chính chạy `./mo trace` (các kiểm tra qua submodule ở T3), `./mo status --all`, và `e2e/`.
6. Bật Dependabot cho hệ `gitsubmodule`, chu kỳ hằng tuần (mục 7.2).
7. Viết lại `CLAUDE.md` và `README.md` theo vai trò umbrella.

**Nghiệm thu:**
```bash
git clone --recurse-submodules git@github.com:<org>/mechops.git /tmp/check && cd /tmp/check
./mo status --all     # test-status gom đủ 49 ID, mỗi ID đúng repo
./mo trace            # xanh, có kiểm qua submodule
```
- `e2e/` rỗng chạy xanh trên CI.
- Dependabot mở được một PR nâng tag thử.

**Quay lui:** revert PR. Thư mục cũ quay lại từ lịch sử, ba repo đội vẫn tồn tại độc lập.

### T7 — Nghiệm thu tổng và bàn giao

**Mục tiêu:** chứng minh ba luồng làm việc của mục 8 chạy đúng với người thật.

**Việc:**

1. Mỗi đội mở một PR thử trong repo của mình. PR merge được mà không cần ai ở đội khác duyệt.
2. Đội robotics mở một PR thử sửa `specs/`. CODEOWNERS bắt buộc một người đội web duyệt.
3. Đội web mở một PR thử sửa `api/openapi.yaml`. CODEOWNERS bắt buộc một người đội mobile duyệt.
4. Founder mở một PR ở repo chính nâng tag agent. PR chỉ merge được khi `e2e/` xanh.
5. Ghi một mục `.steering` ở repo chính, đánh dấu việc tách đã đóng và trỏ về ADR-0019.

**Nghiệm thu:** cả bốn PR thử chạy đúng như mô tả. Từ đây M0' mở lại trong các repo đội: hợp đồng và phía agent ở `mechops-agent`, phía server và deploy ở `mechops-platform`.

## 7. File mẫu

### 7.1 `mechops.repo.toml`

```toml
# repo chính
name = "mechops"
role = "umbrella"
adr_prefix = ""                  # ADR-0020, ADR-0021, ...
submodules = ["repos/platform", "repos/agent", "repos/mobile"]
catalog = "e2e/test-catalog.md"
```

```toml
# mechops-agent
name = "mechops-agent"
role = "team"
team = "robotics"
visibility = "public"
adr_prefix = "ROB"
catalog = "docs/test-catalog.md"
publishes = ["spec"]             # tag spec-vX.Y.Z
```

```toml
# mechops-platform
name = "mechops-platform"
role = "team"
team = "web"
adr_prefix = "WEB"
catalog = "docs/test-catalog.md"
publishes = ["api"]              # tag api-vX.Y.Z
consumes = { spec = "spec-v0.1.0" }
```

```toml
# mechops-mobile
name = "mechops-mobile"
role = "team"
team = "mobile"
adr_prefix = "MOB"
catalog = "docs/test-catalog.md"
consumes = { api = "api-v0.0.1" }
```

### 7.2 `.gitmodules` và Dependabot của repo chính

```ini
[submodule "repos/platform"]
	path = repos/platform
	url = git@github.com:<org>/mechops-platform.git
[submodule "repos/agent"]
	path = repos/agent
	url = git@github.com:<org>/mechops-agent.git
[submodule "repos/mobile"]
	path = repos/mobile
	url = git@github.com:<org>/mechops-mobile.git
```

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: gitsubmodule
    directory: /
    schedule: { interval: weekly }
```

### 7.3 CODEOWNERS

Trên GitHub, một dòng liệt kê nhiều owner thì chỉ cần **một** người trong số đó duyệt. Vì vậy, chỗ nào cần đội kia duyệt thì dòng đó chỉ ghi đội kia. Đội tác giả vẫn tự review trong nội bộ như mọi PR.

```
# mechops-agent
*                 @<org>/robotics
/specs/           @<org>/web
```

```
# mechops-platform
*                           @<org>/web
/api/openapi.yaml           @<org>/mobile
/server/internal/policy/    @<org>/robotics
/server/internal/health/    @<org>/robotics
```

```
# mechops-mobile
*                 @<org>/mobile
```

```
# mechops (repo chính)
*                 @<founder>
```

### 7.4 Branch protection, giống nhau ở cả bốn repo

| Nhánh | Luật |
|---|---|
| `develop` | bắt buộc qua PR; bắt buộc check `verify`; bắt buộc code owner duyệt; cấm force-push |
| `main` | như `develop`, và chỉ founder merge (constitution #9) |

### 7.5 Quy ước tag

| Tag | Ở đâu | Nghĩa |
|---|---|---|
| `vX.Y.Z` | mọi repo | bản phát hành của repo đó; repo chính ghim submodule vào đây |
| `spec-vX.Y.Z` | agent | phiên bản hợp đồng MQTT, Probe API và HTTP mà agent gọi |
| `api-vX.Y.Z` | platform | phiên bản API REST/SSE cho dashboard, mobile và robotics-backend |
| `coord-vX.Y.Z` | robotics-backend | phiên bản Coord API và sự kiện điều phối mà platform dùng (ADR-0020) |
| `pre-split` | repo chính | điểm quay về trước khi tách; ADR bất biến từ đây |

Hợp đồng theo semver: bản minor chỉ được thêm, bản major cần ADR ở repo chính.

## 8. Làm việc sau khi tách

**Việc của một đội** (phần lớn công việc):
1. PR trong repo của đội, đội đó tự duyệt.
2. Merge, đánh tag khi cần phát hành.
3. Dependabot mở PR nâng tag ở repo chính. Founder merge khi `e2e/` xanh.

**Đổi hợp đồng giữa robot và server:**
1. PR sửa `specs/` ở repo agent, kèm test vector. Đội web bắt buộc duyệt.
2. Merge, đánh tag `spec-vX.Y.Z`.
3. Hai đội làm song song: agent implement trong repo agent; platform chạy `./mo spec sync spec-vX.Y.Z` rồi implement.
4. Hai bên phát hành, rồi repo chính nâng cả hai tag trong một PR, merge khi `e2e/` xanh.

**Đổi API cho mobile:**
1. Đội mobile ghi yêu cầu bằng một PR sửa `api/openapi.yaml` ở repo platform, hoặc đội web tự mở PR đó. Đội mobile bắt buộc duyệt.
2. Merge, đánh tag `api-vX.Y.Z`.
3. Đội web implement server; đội mobile chạy `./mo api sync api-vX.Y.Z` rồi làm phần app.

Không đội nào phải chờ đội kia, ngoại trừ PR hợp đồng ở bước 1.

## 9. Rủi ro và đường quay lui

| Rủi ro | Dấu hiệu | Xử lý |
|---|---|---|
| Lịch sử agent lộ bí mật khi chuyển public | `gitleaks` báo ở T4 | dừng, dọn bằng `filter-repo` khi repo còn private, quét lại |
| Bộ công cụ không chạy được ở nhiều repo | T3 quá 5 ngày | dừng tách, giữ monorepo với CODEOWNERS, viết ADR ghi lý do |
| Hỏng giữa T4 và T6 | repo đội không xanh | repo chính chưa xoá gì tới T6, làm việc tiếp từ tag `pre-split` |
| Tính năng xuyên đội kẹt giữa các PR | M3 trễ vì chờ thứ tự | chỉ PR hợp đồng là tuần tự; mọi việc khác song song |
| Nâng tag submodule bị bỏ quên | repo chính tụt nhiều tag | Dependabot hằng tuần; `./mo status --all` cảnh báo khi tụt quá hai tag |
| Thành viên nhầm repo khi mở PR | PR sửa code đội khác | quyền `write` chỉ cấp cho repo của đội (T1) |

## 10. Founder cần quyết trước T0

1. **Tên GitHub Organization**, và tài khoản nào sở hữu nó.
2. **ADR-0019 có vào repo public không.** Mặc định là có, vì nó giải thích vì sao `specs/` nằm ở agent. ADR này có nêu tên các repo private. Nếu không, mục 3.2 bỏ dòng ADR-0019 và bản sao còn 12.
3. **Bộ đo module có giữ không.** Giữ thì đưa vào git ở T0. Bỏ thì `master-plan.html` không còn bảng trạng thái module tự động.
4. **Plan `m1-contract-v01`** nên `keep` hay `abandon`. Thư mục plan ở lại repo chính trong cả hai trường hợp. Nếu việc còn làm tiếp, plan mới mở trong repo agent sau T4.
