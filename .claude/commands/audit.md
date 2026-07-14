---
description: Chạy 2 kiểm toán viên trước khi commit
---
Chạy subagent spec-guardian review toàn bộ diff hiện tại, sau đó subagent test-auditor
kiểm tra các test ID vừa tick trong phiên. Báo cáo PASS/FAIL của cả hai.
Nếu cả hai PASS: commit với message chứa dòng "Implements: <các ID>". Nếu FAIL: liệt kê
vi phạm và dừng.
