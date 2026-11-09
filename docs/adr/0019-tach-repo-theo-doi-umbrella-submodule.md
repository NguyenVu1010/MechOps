# ADR-0019: Tách repo theo đội kỹ năng, repo chính là umbrella ghim submodule theo tag
- Status: accepted
- Date: 2026-11-08
- Covers: []

## Context

Founder muốn ba đội làm việc không phải review chéo nhau. Mỗi đội có kỹ năng riêng:

- **web**: Go và TypeScript. Đội này làm server, dashboard và deploy.
- **robotics**: Rust, C++ và ROS 2. Đội này làm agent, probe, mô phỏng, và sau này cả service điều phối.
- **mobile**: làm ứng dụng mobile, client của cùng API với dashboard.

Ngày 2026-11-08 repo có rất ít mã:

| Thành phần | Trạng thái |
|---|---|
| Go | 22 dòng |
| Rust | chưa có |
| `dashboard/` | rỗng |
| Test | 0/49 |

Như vậy đây là lúc tách rẻ nhất. Trong khi đó, bộ luật, ADR, tracker và `.steering` đã khá đầy. Hai thứ này phải đi theo khi tách.

Ràng buộc có sẵn:

- **Open-core (ADR-0002):** agent và hợp đồng của nó là Apache 2, public. Server, dashboard và OTA orchestration là phần đóng.
- **Hợp đồng giữa hai phía robot và server đã là văn bản máy đọc:** `specs/` gồm AsyncAPI, JSON Schema và test vector. ADR-0016 thêm một hợp đồng HTTP mà agent gọi, gồm enroll và renew.
- **Có logic do robotics quyết mà lại chạy trong server Go:** khi nào coi một robot là khỏe, và chính sách rollout. Hai thứ này không được để đội web tự đoán.

## Options đã cân nhắc

1. **Giữ monorepo, chia quyền bằng CODEOWNERS.** Rẻ nhất. Nhưng mỗi PR vẫn mở trước mặt cả ba đội, CI chạy cả bốn ngôn ngữ, và ranh giới open/closed chỉ dựa vào kỷ luật.
2. **Tách UI khỏi backend**, kèm một repo hợp đồng. Frontend vẫn phải hiểu server, nên review chéo không giảm mà chỉ dời sang PR hợp đồng. Không khớp với cách chia đội.
3. **Hai repo theo kỹ năng, không có repo chính.** Không còn chỗ trung lập cho ADR toàn hệ, catalog và test E2E. Chúng sẽ phải nằm nhờ một trong hai repo.
4. **Repo chính (umbrella) và các repo đội, gắn vào bằng git submodule ghim theo tag.** Làm theo cách Android quản bằng manifest và ROS quản bằng distro `.repos`.
5. **Như phương án 4 nhưng dùng manifest `.repos` với vcstool thay cho submodule.** Đội robotics quen sẵn công cụ này. Nhưng GitHub và Dependabot không đọc được manifest, và repo chính sẽ không tự chứa commit chính xác của từng repo.

## Decision

Chọn phương án 4.

### Các repo

| Repo | Quyền | Đội | Chứa | ADR riêng | Tạo khi |
|---|---|---|---|---|---|
| `mechops` (repo hiện tại) | private | founder | constitution, ADR toàn hệ, `.steering` toàn hệ, catalog gom, `e2e/`, submodule | `ADR-NNNN` | có sẵn |
| `mechops-platform` | private | web | `server/`, `protocol/` (mã sinh), `dashboard/`, `deploy/`, `api/openapi.yaml` | `WEB-NNNN` | lúc tách |
| `mechops-agent` | **public**, Apache 2 | robotics | `agent/`, `probe/`, `sim/`, **`specs/`**, `docs/protocol-notes.md` | `ROB-NNNN` | lúc tách |
| `mechops-mobile` | private | mobile | ứng dụng mobile | `MOB-NNNN` | lúc tách, chỉ có khung |
| `mechops-robotics-backend` | private | robotics | điều phối giao thông, phân công nhiệm vụ, bản đồ (cargo workspace) | `ROB-NNNN` | sau M6 |

Repo điều phối của robotics **không** được đặt tên có chữ "fleet". Lý do: "Fleet Manager" đã là tên của phần điều phối OTA trong server (ADR-0002, ADR-0015, OTA-09), và phần đó vẫn ở platform.

### Repo chính là nơi tích hợp, không phải nơi code hằng ngày

- **Mỗi đội chỉ clone repo của mình.** Repo chính dành cho founder, CI tích hợp và Claude.
- **Submodule chỉ trỏ vào tag release**, không bao giờ trỏ vào đầu nhánh.
  - Muốn đổi tag thì phải mở PR, và PR chỉ được merge khi `e2e/` xanh.
  - Dependabot (hệ `gitsubmodule`) tự mở PR nâng tag.
  - Vì vậy mỗi commit của repo chính là một **phiên bản hệ thống đã kiểm**.
- **`./mo` của repo chính gom thông tin từ các submodule.** Lệnh `./mo steer index --all` và `./mo status --all` đọc ADR, `.steering`, catalog và tracker của từng repo con, rồi sinh ra INDEX, HISTORY và test-status chung. Kết quả do máy sinh, không sửa tay, giống luật hiện hành.

### Hợp đồng

| Hợp đồng | Nằm ở | Bên dùng | Đồng bộ bằng |
|---|---|---|---|
| MQTT (AsyncAPI và schema), Probe API, HTTP mà agent gọi (enroll, renew) | `mechops-agent/specs/` | platform | `./mo spec sync <tag>`: sinh mã Go vào `protocol/`, ghi tag vào `protocol/SPEC_VERSION`, CI kiểm mã sinh khớp tag |
| REST và SSE cho người dùng | `mechops-platform/api/openapi.yaml`, phát hành theo tag `api-vX.Y` | dashboard (cùng repo), mobile, robotics-backend | `./mo api sync <tag>`: sinh client TS hoặc Rust |

- **Không repo đội nào dùng submodule của repo đội khác.** Submodule chỉ xuất hiện ở repo chính.
- **`protocol/` (Go) là mã sinh trong platform.** Phần open của hợp đồng là `specs/`, không phải mã Go sinh ra từ nó (ADR-0002).
- **Quy tắc phiên bản cho cả hai hợp đồng** là semver:
  - Bản minor chỉ được thêm field tùy chọn.
  - Server chấp nhận cả N và N-1.
  - Agent và app mobile khai phiên bản khi kết nối.
  - Bản major cần một ADR của repo chính.
- **CODEOWNERS:**
  - Mọi PR sửa `specs/` cần một người đội web duyệt.
  - Mọi PR sửa `api/openapi.yaml` cần một người đội mobile duyệt.
  - Hai thư mục `server/internal/policy/` và `server/internal/health/` cần một người đội robotics duyệt. Đây là logic Go thuần, không I/O, implement đúng `specs/policies/` và test vector do đội robotics viết.
  - Ngoài các chỗ trên, không còn review chéo nào.

### ADR

- **ADR-0001 đến ADR-0019 nằm nguyên trong repo chính.** Repo chính tiếp tục đánh số `ADR-NNNN` cho các quyết định chạm từ hai repo trở lên, hoặc chạm hợp đồng hay constitution.
- **Repo đội đánh số riêng:** `WEB-`, `ROB-`, `MOB-`.
  - ADR của repo đội không được lật một ADR của repo chính. Muốn lật thì phải viết ADR ở repo chính.
  - `./mo trace` của repo chính kiểm luật này qua submodule.
- **Mỗi repo đội giữ bản sao chỉ-đọc của các ADR liên quan tới nó**: ADR toàn hệ cộng ADR của đội đó. Bộ công cụ (`trace`, skill trỏ ADR) cần đọc được ADR ngay trong repo, và repo agent public cần chúng cho người ngoài. Danh sách ở `docs/product/09-tach-repo.md`.
  - CI của repo chính kiểm bản sao khớp bản gốc.

### Đợt chuẩn hoá ADR trước khi tách

Founder cho phép, một lần duy nhất, sửa trực tiếp ADR 0001–0019 để repo chính nhận một chuỗi quyết định sạch. Đây là ngoại lệ có chủ đích với constitution #8.

- **Không có ADR nào chồng lên nhau một phần.** Các cặp trước đây "supersede một phần" được viết lại cho mỗi ADR chỉ giữ một quyết định:
  - ADR-0009 chỉ còn server.
  - ADR-0004 không còn chọn ngôn ngữ probe.
  - ADR-0018 mô tả thẳng cấu hình Jazzy đang chạy.
  - ADR-0002 có danh sách thư mục open đúng với cách chia repo.
- **Số ADR giữ nguyên.** Các mục `.steering` đã đóng trỏ tới số ADR và không được sửa.
- **Mỗi ADR đã sửa có một dòng `Chuẩn hoá 2026-11-08` ở cuối**, nói bản gốc khác gì. Lịch sử đầy đủ nằm trong git.
- **Cửa sửa đóng tại tag `pre-split`.** Sau đó constitution #8 áp dụng nguyên vẹn: đổi ý thì viết ADR mới. Ở bước T3, luật này có chốt chặn máy: CI từ chối thay đổi nội dung ADR đã accepted, chỉ cho sửa dòng Status khi có ADR mới supersede.

### Test ID

Một ID thuộc về repo nơi bài test của nó chạy được mà không cần repo khác:

- Chỉ cần agent, probe và một broker trần: ID thuộc `mechops-agent`.
- Chỉ cần server, broker và DB: ID thuộc `mechops-platform`.
- Cần cả agent thật và server thật để thấy kết quả: ID là E2E, thuộc `e2e/` của repo chính.

Mỗi repo giữ catalog phần của mình. Repo chính gom các phần thành `05-test-catalog.md` và kiểm không có ID nào thuộc hai repo. Bảng chia 49 ID hiện có nằm ở `docs/product/09-tach-repo.md`.

### Ngoại lệ đóng băng `tools/`

Master plan đóng băng `tools/` cho tới khi TEL-03 xanh. ADR này mở một ngoại lệ có giới hạn:

- Chỉ cho các thay đổi mà việc tách bắt buộc phải có:
  - Tracker và trace đọc cấu hình theo repo.
  - Lệnh `spec sync`, `api sync`, và các lệnh gom `--all`.
  - Tiền tố ADR.
- Mỗi thay đổi phải có chốt chặn máy kiểm, theo ADR-0011.
- Hạn chót là ngày nghiệm thu tách repo.

### Lịch sử git

- `mechops-platform` và `mechops-agent` được rút ra bằng `git filter-repo` theo thư mục, nên giữ được log và blame.
- Trước khi đặt `mechops-agent` thành public phải quét toàn bộ lịch sử bằng gitleaks. Lịch sử đã public thì không rút lại được.
- Repo chính xoá các thư mục đã chuyển đi bằng một commit thường, không viết lại lịch sử. Tag `pre-split` đánh dấu điểm quay về.

## Consequences

+ Mỗi đội có repo, CI và ngôn ngữ của riêng mình. Review chéo chỉ còn ở ba chỗ có chủ đích: `specs/`, `api/openapi.yaml`, và `policy/` cùng `health/`.
+ Ranh giới open/closed trùng với ranh giới repo. Mã đóng không thể vô tình lọt vào repo public.
+ Mỗi commit của repo chính trả lời được câu "những phiên bản này chạy được với nhau".
+ Khi đội mobile hoặc robotics-backend xuất hiện, chỉ cần thêm một submodule, không phải tổ chức lại.
− Một tính năng xuyên đội cần ba đến bốn PR theo thứ tự: spec, rồi hai phía, rồi nâng tag ở repo chính. Ca nặng nhất là M3 (OTA).
− Bộ công cụ `./mo` phải chạy được ở bốn repo với bốn bộ ngôn ngữ khác nhau. Đây là việc lớn nhất của đợt tách, và là lý do phải mở ngoại lệ đóng băng `tools/`.
− M0' lùi khoảng hai tuần, vì việc tách được làm trước.
− CODEOWNERS theo đội cần một GitHub Organization. Bảo vệ nhánh (ruleset) trên repo private cần gói trả phí: GitHub Pro cho tài khoản cá nhân, hoặc gói Team cho Organization. Gói miễn phí chỉ bảo vệ được repo public.
