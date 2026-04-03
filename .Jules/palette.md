## 2026-04-02 - Glassmorphic Keyboard Shortcuts for Global Nav
**Learning:** Adding subtle, visually appealing (glassmorphic) `<kbd>` elements to labels with global shortcuts (like 'S' for System Model) significantly improves the discoverability of keyboard interactions for power users, without cluttering the UI. Pairing it with `.focus()` logic and `aria-hidden="true"` with a visually hidden explanatory span keeps it accessible.
**Action:** Use this pattern of `[Label Text] <kbd aria-hidden="true">Key</kbd> <span class="sr-only">Press Key to focus</span>` for other primary global controls across the application.

## 2026-04-03 - CSS-only Loading States via aria-busy
**Learning:** Hardcoding visual loading states (like `opacity: 0.5` or `pointer-events: none`) in JavaScript couples logic and styling and is prone to errors. Using CSS pseudo-elements (`::after`) triggered solely by toggling an `aria-busy` attribute on the container creates a much cleaner, more reliable, and semantic loading indicator (such as a visual spinner) while maintaining accessibility.
**Action:** Use CSS pseudo-elements driven by standard ARIA attributes (like `aria-busy="true"`) for async operation states instead of inline JavaScript style manipulation.
