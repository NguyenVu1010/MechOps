# e2e/ — test cần agent thật và server thật cùng chạy

Test ID ở đây chỉ quan sát được khi hai repo đội ghép lại (ADR-0019): PRV-01..05,
TEL-03, TEL-04, TRM-01, TRM-03, TRM-04, LOD-01..03.

Mỗi lần chạy, E2E dùng đúng phiên bản các submodule đang ghim trong `repos/`:
platform dựng bằng compose của nó, agent lấy từ bản phát hành cùng tag. PR nâng tag
submodule chỉ merge khi E2E xanh.

Chưa có test. Bài đầu tiên là PRV-01 (enroll token hợp lệ) ở M1; ngôn ngữ và cách
dựng harness quyết khi làm bài đó.
