# ADR-0011: Mỗi luật của repo phải có một chốt chặn máy kiểm, không chỉ một dòng văn bản
- Status: accepted
- Date: 2026-08-23
- Covers: []

## Context

Tính tới 2026-08-23, repo có `constitution.md` (9 nguyên tắc), 9 ADR, catalog 49 test ID,
5 skill, 2 subagent — bộ doctrine đầy đủ. Nhưng khi rà lại, hầu hết các luật **chỉ tồn tại
dưới dạng văn bản**:

| Luật | Cưỡng chế trước ADR này |
|---|---|
| #1 TDD, test đỏ trước | không có |
| #2 Tick chỉ do máy | hook chặn `test-status` — nhưng hook đang hỏng (ADR-0010) |
| #4 Spec thắng code | subagent `spec-guardian`, chỉ chạy khi agent nhớ gọi |
| #5/#6 Dependency mới phải có ADR | không có |
| #7 agent không import server | không có |
| Catalog #1 mỗi PR khai test ID | không có |

Và `.github/workflows/pr.yml` là hai dòng `echo "TODO(M0)"`. Nghĩa là toàn bộ kỷ luật
đang dựa vào việc agent tự nguyện tuân thủ văn bản nó vừa đọc.

Đây là một chế độ vận hành có thật, nhưng nó thất bại đúng vào lúc tệ nhất: khi ai đó
vội, khi context dài và văn bản đã trôi khỏi tầm nhớ, khi bản build cuối trước demo cần
xanh gấp. Văn bản không phòng thủ được vào lúc đó — chỉ có máy mới làm được.

## Options đã cân nhắc

1. **Giữ nguyên, dựa vào review của người.** Team 1–2 người, founder đọc mọi PR. Nhưng
   `docs/DEVELOPMENT.md` tự đặt ngân sách 5 phút/PR — 5 phút không đủ để kiểm 9 nguyên
   tắc bằng mắt, và toàn bộ mục đích của evidence là để founder *không phải* đọc từng dòng.
2. **Thêm subagent chuyên kiểm từng luật.** `06-spec-management.md` đã chốt đúng 2 subagent
   và lý do vẫn đúng. Thêm nữa là tăng chi phí mỗi phiên để mua một thứ mà `grep` làm được.
   Và LLM kiểm luật xác định được bằng cú pháp là dùng sai công cụ.
3. **Mỗi luật xác định được → một chốt chặn máy; luật cần phán đoán → subagent.** ← chọn

## Decision

Phân tuyến theo bản chất của luật, không theo độ quan trọng:

**Luật xác định được bằng cú pháp → chốt chặn máy, chạy trong CI:**

| Luật | Chốt chặn |
|---|---|
| #2 tick chỉ do máy | hook `PreToolUse` (bash thuần) + CI render lại `.md` từ `.json` rồi `git diff --exit-code` |
| #5/#6 dependency có ADR | `./mo trace` — skill trỏ ADR không tồn tại/đã supersede = lỗi |
| #7 chiều phụ thuộc | `golangci-lint` rule `depguard` |
| quy ước slog | `golangci-lint` rule `forbidigo` |
| catalog #1 khai test ID | `.githooks/commit-msg` + CI quét lại toàn bộ commit của PR |
| milestone khớp catalog | `./mo trace` đối chiếu `track.py` với `05-test-catalog.md` |
| nuốt lỗi, resource leak | `errcheck`, `errorlint`, `bodyclose`, `sqlclosecheck`, `rowserrcheck` |

**Luật cần phán đoán → vẫn là người hoặc subagent:**
lệch ngữ nghĩa spec (`spec-guardian`), test rỗng-mà-pass (`test-auditor`), mức nghiêm
trọng khi review (`REVIEW.md`), và mọi thứ ở constitution #9 (merge, sửa `specs/`,
tick [H], release).

Hai quy tắc kèm theo:

- **Chốt chặn phải nêu lý do, không chỉ nêu lỗi.** Mọi thông báo chặn dẫn về điều
  constitution hoặc quy tắc catalog tương ứng. Một chốt chặn không giải thích được vì
  sao nó tồn tại sẽ bị vô hiệu hoá vào lần đầu tiên nó gây phiền.
- **Hook local là để biết sớm, CI là chốt chặn cuối.** Hook local bị `--no-verify` được;
  CI thì không. Mọi kiểm tra chạy ở hook đều chạy lại trong CI.

Không dùng `anthropics/claude-code-action` để review PR ở giai đoạn này: cần secret trong
repo và tốn token mỗi PR, trong khi `REVIEW.md` + `/code-review` local cho cùng chất lượng
đọc mà chi phí nằm trong phiên đang có. Xét lại khi có người thứ ba vào dự án.

## Consequences

+ Mỗi luật có một địa chỉ trả lời được câu "cái gì bắt lỗi này": bảng trên là địa chỉ đó.
+ Vi phạm bị chặn trong vài giây ở local thay vì vài ngày ở review.
+ Founder review được trong 5 phút vì phần kiểm cơ học đã xong trước khi PR mở.
− CI chậm hơn (lint + `-race` + trace). Chấp nhận: chạy khi người đang làm việc khác.
− Chốt chặn sai sẽ chặn việc đúng. Giảm bằng cách mọi chốt chặn đều nêu lý do và đều có
  đường vượt tường minh (ví dụ `Implements: none`), không có đường vượt im lặng.
− Bộ linter và các script `tools/checks`, `tools/report` là mã phải bảo trì.
