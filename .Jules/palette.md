## 2026-04-02 - Glassmorphic Keyboard Shortcuts for Global Nav
**Learning:** Adding subtle, visually appealing (glassmorphic) `<kbd>` elements to labels with global shortcuts (like 'S' for System Model) significantly improves the discoverability of keyboard interactions for power users, without cluttering the UI. Pairing it with `.focus()` logic and `aria-hidden="true"` with a visually hidden explanatory span keeps it accessible.
**Action:** Use this pattern of `[Label Text] <kbd aria-hidden="true">Key</kbd> <span class="sr-only">Press Key to focus</span>` for other primary global controls across the application.

## 2026-04-03 - CSS-Driven Async Loading States via `aria-busy`
**Learning:** Hardcoding visual loading states (like `opacity: 0.5; pointer-events: none;`) directly in JavaScript logic creates jank and tight coupling. By instead setting `aria-busy="true"` on a container and using CSS pseudo-elements (`::after`) to render a glassmorphic spinner, the UI is decoupled from the JS logic, making the component both visually smoother and inherently more accessible.
**Action:** Always avoid inline JavaScript style mutations for UI states; use semantic ARIA attributes to trigger CSS-based visual feedback.
## 2024-05-24 - [Tactile Shortcut Feedback & Focus Traps]
**Learning:** Global keyboard shortcuts (like 's' to focus) can create an A11y focus trap if they don't explicitly ignore native interactive elements like `<select>`. Pressing the shortcut while inside a select overrides the native jump-to-letter search feature. Additionally, visually rendered `<kbd>` elements lack the tactile feedback of physical keys, making shortcut triggers feel disconnected from the UI.
**Action:** When adding global shortcuts, ALWAYS verify `document.activeElement.tagName` against `['INPUT', 'TEXTAREA', 'SELECT']`. Furthermore, provide tactile feedback by applying a brief scale down animation (e.g., `transform: scale(0.85)`) to the corresponding `<kbd>` indicator via JS timeouts.

## 2026-04-10 - Dynamic Context Synchronization for Interactive Visualizations
**Learning:** When interactive visualizations update asynchronously via global controls (e.g., a system dropdown), static headings and `aria-label`s lose context, confusing both visual and screen reader users about what is currently displayed. Dynamically appending the active selection (e.g., "Phase Portrait: Lorenz") to both the visual `<h2>` tags and the container's `aria-label`s keeps the context synced and accessible.
**Action:** When implementing interactive data visualizations, ensure that section headings and descriptive ARIA labels are bound to the underlying state and update dynamically alongside the data.
