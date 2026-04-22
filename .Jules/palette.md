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

## 2025-04-13 - Improved Affordances and Disabled State Feedback
**Learning:** Adding `cursor: pointer` to labels strongly improves perceived clickability. Additionally, disabling input elements (like a `select` dropdown) during asynchronous loading can trap users without feedback; adding a `title="Loading..."` provides native tooltip feedback explaining the disabled state.
**Action:** When creating forms or interactive controls, always ensure labels use `cursor: pointer` and temporarily disabled controls include a descriptive `title` attribute to explain the unresponsiveness.

## 2026-04-14 - Handling `prefers-reduced-motion` in WebGL/Canvas
**Learning:** Standard CSS `@media (prefers-reduced-motion: reduce)` media queries successfully disable CSS-based animations and transitions, but they do NOT apply to or automatically pause JavaScript-driven animations running inside `<canvas>` elements (like Three.js or D3 `requestAnimationFrame` loops). Vestibular triggering can still occur from continuous 3D rendering even if the rest of the page respects the user's OS settings.
**Action:** When working with continuous `<canvas>` animations, explicitly query `window.matchMedia('(prefers-reduced-motion: reduce)').matches` inside the `requestAnimationFrame` render loop to pause or severely restrict the animation logic when true.

## 2026-04-15 - Chart.js Tooltips with Hidden Points
**Learning:** For performance reasons, high-density line charts often hide individual data points (e.g., `pointRadius: 0` in Chart.js). However, hiding points completely disables the default hover interaction that relies on intersecting the mouse with a point, effectively breaking tooltips and removing a critical layer of interactive data discovery.
**Action:** When hiding points on a line chart for performance, ALWAYS restore tooltip accessibility by explicitly configuring the chart's interaction mode to trigger on vertical slicing rather than point intersection (e.g., `interaction: { mode: 'index', intersect: false }`).

## 2026-04-16 - Dynamic Context Initialization on Load
**Learning:** Hardcoding static text in HTML for headings or `aria-label`s that are inherently bound to dynamic state (like a default dropdown selection) is dangerous because the source of truth is split. While it visually fixes the initial render, it is brittle. Instead, extracting the context synchronization logic into a reusable function (e.g., `syncContextLabels()`) and invoking it explicitly on `DOMContentLoaded` guarantees that the UI exactly reflects the underlying interactive state from the very first paint, without hardcoded mismatches or hacky synthetic event dispatches.
**Action:** When working with dynamic visualizations or UI sections whose titles depend on form controls, always initialize their labels via a shared state-sync function upon load, rather than hardcoding default assumptions into the static HTML.

## 2026-04-17 - Contextual Axis Labels and High-Contrast Typography in Data Visualizations
**Learning:** Default D3.js or Chart.js axes often lack contextual labels indicating what dimensions represent (e.g., whether axes map to generic states x1/x2 or specific physical states like angle θ/angular velocity ω), leading to cognitive load when switching datasets. Furthermore, default SVG axis colors can fail WCAG contrast checks against dark backgrounds, and standard system fonts can break design consistency.
**Action:** Enhance D3.js data visualizations by explicitly appending contextual text labels (e.g., `x` and `y` or specific parameter names) to axes. Additionally, ensure SVG axis elements explicitly apply high-contrast colors (e.g., `.attr("color", "#ccc")`) and inherit typography (e.g., `.style("font-family", "inherit")`) in the rendering chain to meet WCAG AA contrast guidelines and match the application's overall design system.

## 2026-04-22 - Document Title Context Synchronization
**Learning:** When dynamically updating core context in a single-page application (like swapping the mathematical model), explicitly updating `document.title` ensures screen reader users and users navigating multiple browser tabs maintain awareness of the active state.
**Action:** When dynamically updating context, ensure `document.title` is also explicitly updated.
