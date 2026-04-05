## 2026-04-02 - Glassmorphic Keyboard Shortcuts for Global Nav
**Learning:** Adding subtle, visually appealing (glassmorphic) `<kbd>` elements to labels with global shortcuts (like 'S' for System Model) significantly improves the discoverability of keyboard interactions for power users, without cluttering the UI. Pairing it with `.focus()` logic and `aria-hidden="true"` with a visually hidden explanatory span keeps it accessible.
**Action:** Use this pattern of `[Label Text] <kbd aria-hidden="true">Key</kbd> <span class="sr-only">Press Key to focus</span>` for other primary global controls across the application.
## 2024-05-18 - Loading States

**Learning:** When updating main content asynchronously, avoid hardcoding visual loading states via inline JavaScript (like `opacity: 0.5` or `pointer-events: none`). Instead, solely toggle `aria-busy="true"` on the container, and use CSS (including pseudo-elements like `::after` for a visual spinner) to handle visual dimming, disabled interactions, and loading indicators. Cleanly remove the ARIA attribute within a `.finally()` block.
**Action:** Always prefer aria-busy attributes combined with CSS for loading states to provide a more robust and accessible experience.
