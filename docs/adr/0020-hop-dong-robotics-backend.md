# ADR-0020: Hợp đồng giữa robotics-backend, platform và robot: lease qua MQTT, lệnh qua REST, không thêm giao thức
- Status: accepted
- Date: 2026-11-10
- Covers: []

## Context

ADR-0019 đặt các service điều phối của đội robotics (giao thông, phân công nhiệm vụ, bản đồ) vào repo riêng `mechops-robotics-backend`. Ngày 2026-11-10 founder chốt thêm:

- Đội làm robotics-backend khác đội web/app.
- Ngôn ngữ có thể khác, CI khác.
- Repo tạm thời đóng.
- Cần một hợp đồng vừa linh hoạt (thêm loại task, thuật toán, loại robot mà platform không phải sửa) vừa ổn định.

ADR-0019 mới cho robotics-backend dùng `api/openapi.yaml` của platform. Như vậy chưa đủ cho điều phối thời gian thực, và nếu mọi field mới của robotics phải đi qua server thì review chéo với đội web quay lại. Câu hỏi "ra lệnh qua platform hay nối thẳng MQTT" nằm trong `BACKLOG.md` từ lúc tách repo.

Ràng buộc có sẵn:

- MQTT 5 qua EMQX một node (ADR-0001, ADR-0003, ADR-0014).
- Tenant nằm trong topic (ADR-0008).
- Danh tính bằng mTLS do CA của server cấp (ADR-0016).
- Spec v2 đã loại gRPC, GraphQL, NATS và Kafka.

## Options đã cân nhắc

1. **Mọi thứ đi qua REST/SSE của platform.** Robotics-backend chỉ là một client.
   - Độ trễ cộng thêm một chặng.
   - Mỗi field mới phải sửa server, nên đội web thành nút cổ chai.
2. **Robot và robotics-backend nói thẳng qua MQTT trên broker hiện có. Platform giao việc qua REST và nhận sự kiện qua MQTT.** ← chọn
3. **gRPC stream giữa mọi module.**
   - Robot phải mở kết nối thứ hai và thêm một cổng mTLS.
   - Không dựng được form từ JSON Schema.
   - Spec v2 đã loại.
4. **Thêm message bus** (NATS JetStream, Zenoh).
   - Phát lại sự kiện tốt hơn.
   - Nhưng là hạ tầng mới trong khi EMQX đủ tải.
   - Zenoh đi qua WAN và NAT kém, không có ACL theo thiết bị (ADR-0001 đã loại).

## Decision

Chọn phương án 2.

### Phạm vi của robotics-backend

Robotics-backend **chỉ cấp quyền đi từng đoạn đường** bằng lease. Việc lái và tránh vật cản tức thời vẫn do robot tự làm (Nav2 trên robot). Nhờ vậy kênh điều phối chịu được độ trễ vài trăm ms, và MQTT đủ dùng. Muốn robotics-backend điều khiển chuyển động trực tiếp thì phải viết ADR mới.

### Ba kênh, mỗi kênh chỉ một bên làm chủ

| Kênh | Giao thức | Đặt ở | Bên làm chủ | Tag | Bên phải duyệt khi sửa |
|---|---|---|---|---|---|
| **A. Coord API**: platform tạo và hủy task, hỏi kế hoạch, bản đồ | HTTP/JSON, OpenAPI, mTLS giữa hai service | `mechops-robotics-backend/api/coord.yaml` | robotics-backend | `coord-vX.Y.Z` | đội web |
| **B. Sự kiện giữa platform và robotics-backend** | MQTT 5, QoS 1, session bền, AsyncAPI | sự kiện của robotics-backend: `mechops-robotics-backend/api/events.yaml`; sự kiện của platform: `mechops-platform/api/events.yaml` | bên phát sự kiện | theo tag của bên phát | bên nhận sự kiện |
| **C. Robot và robotics-backend**: lease, đặt chỗ, tiến độ | MQTT 5, dùng chung kết nối agent đang có | `mechops-agent/specs/`, nhóm topic `coord/` | đội agent | `spec-vX.Y.Z` | đội robotics-backend |

Topic theo đúng layout của ADR-0008:

- Kênh C: `mechops/v1/{tenant}/devices/{deviceId}/coord/...`
  - Agent chỉ được chạm `{deviceId}` của chính nó, bằng ACL đang có.
  - Robotics-backend được chạm `devices/+/coord/#`.
- Kênh B: `mechops/v1/{tenant}/services/{service}/events/...`, với `{service}` là `platform` hoặc `coord`.

Tên topic chi tiết chốt trong AsyncAPI của từng repo.

### Giao thức cho từng cặp module

| Cặp | Giao thức |
|---|---|
| Robot ↔ robotics-backend | Kênh C |
| Platform → robotics-backend | Kênh A |
| Sự kiện qua lại | Kênh B |
| Chọn bên chỉ huy giữa các instance robotics-backend | PostgreSQL advisory lock. Không thêm etcd hay Consul |
| Dừng khẩn | Dashboard → platform (REST) → agent (kênh lệnh MQTT hiện có). **Không đi qua robotics-backend** |
| Phát bản đồ | HTTPS tải theo URI kèm digest, cùng cơ chế với artifact OTA (ADR-0015). MQTT chỉ báo có bản mới |
| Giữa các phần trong robotics-backend | Gọi hàm trong cùng một tiến trình (mỗi phần là một crate). Không tách thành nhiều service khi chưa có số đo cần tách |
| Dashboard, mobile ↔ platform | Giữ REST + SSE (ADR-0007). Trạng thái điều phối tới dashboard qua SSE do platform chuyển tiếp |
| Agent ↔ probe | Giữ Unix socket NDJSON (ADR-0004). Robotics-backend không chạm thẳng vào ROS |

Payload là JSON. Mỗi tin mang `content-type` và phiên bản trong user property của MQTT 5, nên sau này đổi sang CBOR được mà không phá hợp đồng.

### Luật an toàn (bắt buộc trong hợp đồng)

1. **Lease có thời hạn.**
   - Robot chỉ đi trong đoạn đã được cấp, và dừng khi lease hết hạn mà chưa được gia hạn.
   - Luật này chạy trong agent và không phụ thuộc mạng.
   - Tin lease mang MQTT 5 `Message Expiry Interval`, để lease cũ kẹt trong hàng đợi không bao giờ được giao.
2. **`epoch` của bên chỉ huy.**
   - Mỗi lệnh mang `epoch`. Số này tăng mỗi lần một instance robotics-backend giành được advisory lock.
   - Agent từ chối lệnh có `epoch` thấp hơn số nó đã thấy.
3. **`id` và `seq`.**
   - Mỗi tin có `id` để bên nhận bỏ bản trùng do QoS 1 giao lại.
   - Mỗi robot, và mỗi luồng sự kiện, có `seq` tăng dần để xếp đúng thứ tự.
4. **Ảnh trạng thái trước, sự kiện sau.**
   - Khi khởi động lại, bên nhận tải ảnh trạng thái qua REST rồi mới nghe sự kiện.
   - Thấy `seq` bị hụt thì tải lại ảnh trạng thái.
   - Hàng đợi của EMQX có giới hạn, nên bước tải lại là bắt buộc, không phải phương án dự phòng.
5. **REST chống race.** Lệnh sửa task dùng `If-Match` theo version của task, cộng header `Idempotency-Key`.
6. **Lớp an toàn cục bộ của robot luôn thắng mọi lệnh điều phối.**
   - Dừng khẩn qua mạng **không phải** E-stop an toàn theo tiêu chuẩn.
   - Robot vẫn phải có nút dừng vật lý và mạch an toàn riêng. MechOps không thay thế chúng.
7. **Robot không khai năng lực `coord` lúc enroll thì được coi là vật cản.** Robotics-backend không gửi lệnh `coord` cho robot đó.

### Phần linh hoạt

- **Lõi cứng nhỏ.** Task gồm `id`, `type`, `state`, `version`, `robots[]`, `params`, `created_at`.
  - Máy trạng thái là cố định: `pending → assigned → running → done | failed | cancelled`.
  - Platform lưu và hiển thị `params` nhưng không diễn giải nó.
- **Danh mục loại task tự mô tả.** `GET /v1/task-types` trả về JSON Schema cho từng loại.
  - Dashboard và mobile dựng form từ schema đó.
  - Thêm loại task mới là bản minor của `coord-v`, không cần commit nào ở platform hay mobile.
  - Mỗi task ghi phiên bản schema lúc nó được tạo.
- **Khai năng lực.** Khi đăng ký với platform, robotics-backend khai `capabilities` (ví dụ `traffic`, `allocation`, `maps`). Platform ẩn tính năng chưa có.
- **Đọc khoan dung.** Gặp field lạ thì bỏ qua. Không dùng lại tên field cũ cho nghĩa mới. Phần dành cho từng hãng robot nằm trong `ext.<vendor>.*`.

### Phần ổn định

- **Luật phiên bản của ADR-0019 áp cho cả kênh A và B:**
  - Bản minor chỉ thêm.
  - Bên nhận chấp nhận N và N-1.
  - Bản major cần ADR của repo chính.
- **Bên làm chủ phát hành kèm test vector**, gồm mẫu request, response và sự kiện. Bên dùng chạy bộ vector trong CI. Cách này không cần thêm thư viện.
- **Chủ dữ liệu:**
  - Platform làm chủ thiết bị, tenant, người dùng và quyền.
  - Robotics-backend làm chủ task, kế hoạch và bản đồ.
  - Không bên nào sửa dữ liệu của bên kia, chỉ được gửi yêu cầu qua kênh A.
- **Ranh giới truy cập:**
  - Robotics-backend không bao giờ nói chuyện với người dùng.
  - Nó vào broker bằng chứng chỉ mTLS riêng, và ACL chỉ cho `devices/+/coord/#` cùng `services/coord/#`.
  - Platform nghe các topic `coord/` để ghi audit.

### Tham số khởi đầu

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| Thời hạn lease | 2 s | gia hạn trước khi đi hết nửa thời hạn |
| Độ trễ từ lúc robot báo vị trí tới lúc nhận lease mới | p99 < 200 ms | với 200 robot báo vị trí ở 10 Hz |

Hai giá trị này nằm trong cấu hình có giá trị mặc định, không viết cứng trong mã. Chỉnh dựa trên số đo của các kịch bản bên dưới thì không cần ADR mới, nếu thời hạn lease vẫn trong khoảng 0,5–5 s. Ra ngoài khoảng đó phải viết ADR mới.

### Kịch bản kiểm chứng

Các kịch bản chạy trên mô phỏng `mechops-agent/sim`, có cắm lỗi chủ động.

| # | Kịch bản | Đạt khi |
|---|---|---|
| 1 | Robotics-backend chết giữa ca | Mọi robot dừng trong ≤ thời hạn lease, không robot nào ra khỏi đoạn đã được cấp |
| 2 | Hai instance cùng ra lệnh | Agent chỉ theo `epoch` cao nhất. Hai robot không giữ cùng một đoạn đường |
| 3 | Hai robot xin cùng ngã tư trong 100 ms | Đúng một robot được cấp. Tin trùng không làm cấp hai lần |
| 4 | Robot rớt mạng 30 s | Robot đó tự dừng. Robot khác được tính lại đường. Khi có mạng lại, robot không tự chạy tiếp |
| 5 | Hủy task đúng lúc đang giao | Kết thúc ở `cancelled`. Robot không nhận việc |
| 6 | Agent N và N-1 chạy chung | Robot không có năng lực `coord` được coi là vật cản |
| 7 | Thêm loại task mới | Form hiện trên dashboard, task chạy hết vòng đời. Không có commit nào ở platform |
| 8 | Platform khởi động lại khi đang có 200 sự kiện | Platform phát hiện hụt và tải lại ảnh trạng thái. Dashboard khớp trạng thái thật |
| 9 | E-stop khi robotics-backend treo nhưng vẫn giữ kết nối | Robot dừng trong ≤ 1 s mà không qua robotics-backend |
| 10 | Tải: 200 robot, 10 Hz | Đạt ngưỡng độ trễ ở bảng tham số |

- Kịch bản 1, 2, 4 và 9 **phải qua trước khi điều phối chạy trên robot thật.**
- Kịch bản 10 quyết định MQTT có còn đủ dùng.
- Các kịch bản cần agent, platform và robotics-backend chạy cùng nhau, nên là test E2E của repo chính (luật Test ID của ADR-0019). Nhóm ID được thêm vào catalog cùng lúc với việc tạo repo robotics-backend.

## Consequences

+ Không thêm giao thức hay thư viện nào ngoài stack. Một broker, một chỗ ACL, một chỗ audit.
+ Thêm loại task, thuật toán hay loại robot không cần đội web và đội mobile viết mã. Review chéo chỉ còn ở kênh A và B, khi chính hợp đồng thay đổi.
+ Hướng hỏng là an toàn: mất robotics-backend, mất broker hay mất mạng đều dẫn tới robot dừng khi lease hết hạn.
− EMQX một node (ADR-0014) thành điểm hỏng chung. Broker chết thì cả đội robot đứng. Muốn chịu được broker chết thì phải quyết lại ADR-0014, việc vốn đã hẹn trước SaaS.
− Agent phải có thêm watchdog lease và kiểm `epoch`. Đây là mã an toàn, cần test riêng ở repo agent.
− Platform phải giữ một bản sao trạng thái task để hiển thị, và chỉ đồng bộ được bằng ảnh trạng thái cộng `seq`. Sẽ có độ trễ hiển thị nhỏ.
− Thêm hai hợp đồng có tag (`coord-v`, sự kiện), nên mỗi tính năng xuyên đội có thể thêm một PR.
