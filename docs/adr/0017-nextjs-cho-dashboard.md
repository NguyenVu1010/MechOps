# ADR-0017: Next.js + TypeScript cho dashboard
- Status: accepted
- Date: 2026-10-18 (hồ sơ hóa từ dev-plan mục 1.4, chốt 2026-07-09)
- Covers: [WLB-01]

## Context

Constitution #5 và 02-dev-plan mục 1.4 đã chốt Next.js 15 + TypeScript + Tailwind +
shadcn/ui + ECharts + TanStack Query, nhưng chưa có ADR. Dashboard đứng sau đăng
nhập, không cần SEO, dữ liệu realtime qua SSE (ADR-0007). Câu hỏi hợp lý mà một dev
mới sẽ hỏi: vì sao không Vite + React thuần, nhẹ hơn và không có server render.

## Options đã cân nhắc (mục đánh * là dựng lại khi hồ sơ hóa)

1. **Next.js (App Router), output `standalone`.** ← chọn
2. **Vite + React + TanStack Router*.** Nhẹ, SPA thuần, không server. Mất route handler
   phía server để proxy SSE/cookie cùng origin; phải thêm nginx hoặc để server Go phục
   vụ static.
3. **SvelteKit*.** Hệ sinh thái component cho dashboard công nghiệp mỏng hơn; shadcn/ui
   là React.

## Decision

Next.js, App Router, build `output: 'standalone'` thành một image Docker không cần
node_modules đầy đủ. Lý do theo thứ tự:

1. **shadcn/ui + Tailwind** là con đường white-label rẻ nhất: component copy vào repo,
   theming bằng CSS variables đọc từ cấu hình instance (WLB-01 không rebuild image).
2. **Route handler cùng origin** cho SSE và cookie phiên: trình duyệt nói chuyện với một
   origin, dashboard proxy sang server Go. Không cần nginx riêng trong Compose.
3. **Hệ sinh thái lớn nhất** để AI sinh code và người review; team TypeScript dễ tuyển.

SSR không phải lý do chọn và không được dùng để render dữ liệu thiết bị: mọi dữ liệu
đi qua TanStack Query + SSE ở client, theo ADR-0007.

Nâng phiên bản major (Next 16+) là việc của plan M2, không cần ADR mới.

## Consequences

+ White-label bằng CSS variables, không rebuild. Một image, một origin.
+ Component library sẵn cho bảng thiết bị, form, dialog.
− Next.js nặng hơn Vite về build time và kích thước image (~150 MB standalone). Chấp
  nhận trên VPS/edge server.
− App Router có đường cong học riêng; giữ dashboard là SPA phía client, dùng server
  component tối thiểu (layout, auth guard) để không kéo team vào tranh luận RSC.
