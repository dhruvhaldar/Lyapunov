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

## 2026-04-23 - Immediate Visual Feedback for Interaction-Driven Pauses
**Learning:** When relying on hover or focus events to pause visual animations (like 3D WebGL scenes) for accessibility, a native `title` attribute is insufficient because it has an unpredictable delay before appearing. The animation stopping can also be misinterpreted as the page freezing or crashing. Providing a distinct, immediate visual indicator (like a fading-in "Paused" badge) upon interaction gives users satisfying confirmation of their action and the system's state.
**Action:** When pausing continuous animations based on user interaction (hover/focus), always provide an immediate, custom visual indicator (e.g., using a CSS `::after` pseudo-element) rather than relying solely on native tooltips or the absence of motion.

## 2026-04-24 - Error Toast Notifications and Visual Feedback Parity
**Learning:** When using `aria-live` for screen reader error announcements, visual users may be completely unaware of silent background fetch failures if the UI simply resets to its previous state. Implementing a transient visual error toast (with `aria-hidden="true"` to prevent double-announcement) ensures parity of feedback between visual and assistive technologies.
**Action:** When adding accessible error announcements, ensure equivalent visual feedback is also provided (like an error toast) to keep sighted users informed of application state.
## 2026-04-25 - Explicit HTML Elements for State Indicators Over Pseudo-Elements
**Learning:** While CSS pseudo-elements (`::after`) provide a quick way to add visual badges (like a "Paused" indicator), injecting textual content via CSS mixes presentation with content. This approach can be less maintainable, limits DOM-level accessibility enhancements (like applying specific ARIA attributes to the badge itself), and complicates localization.
**Action:** When implementing visual state indicators, prefer adding concrete HTML elements to the DOM and controlling their visibility via CSS rather than relying purely on CSS `content` properties.

## 2026-04-26 - Semantic Landmarks for Interactive Visualizations
**Learning:** When grouping distinct interactive visualizations (like charts or 3D views) within layout containers, applying `role="region"` and an `aria-labelledby` attribute pointing to the section's heading ID converts the containers into semantic landmarks. This significantly improves document structure and navigability for screen reader users by allowing them to quickly jump between distinct visualization zones.
**Action:** Always apply `role="region"` and `aria-labelledby` to major visualization containers that are grouped by a specific heading.

## 2026-04-27 - Zero-Dependency Interactive Data Discovery via Native Tooltips
**Learning:** For dense data visualizations like phase portraits mapped in SVG using D3, implementing complex custom tooltips using heavy external libraries can decrease performance and overcomplicate the DOM. However, hiding the data behind anonymous graphics limits user discovery. Injecting native SVG `<title>` elements mapped to each vector line and combining them with simple CSS hover affordances (e.g., `stroke-width` transitions and `cursor: crosshair`) provides a zero-dependency, lightweight, and effective way for users to discover the underlying mathematical state (like vector components and magnitudes).
**Action:** When creating dense SVG-based data visualizations, consider appending native `<title>` elements to individual graphical marks along with CSS hover styles for an immediate, lightweight interactive data discovery experience before reaching for complex tooltip libraries.

## 2026-05-02 - Keyboard Shortcut Screen Reader Hints
**Learning:** Adding screen-reader-only shortcut hints inside `<label>`s is an anti-pattern. If a user focuses on the corresponding input, they will often hear the label read aloud again along with the shortcut, creating redundant and confusing auditory clutter. The `aria-keyshortcuts` attribute is specifically designed to handle this cleanly on the input itself.
**Action:** Use the `aria-keyshortcuts` attribute directly on the interactive element (e.g., `<select>`, `<button>`) instead of injecting visually hidden text into its associated `<label>`.

## 2026-05-03 - Promise Error Swallowing Breaks Global UI Error State
**Learning:** When `fetch` calls implicitly swallow HTTP errors (by not checking `!response.ok` or by catching and not re-throwing in local `.catch()` blocks), aggregator logic like `Promise.all` in the main UI file will resolve successfully. This completely breaks global error handling (like displaying a fallback toast and announcing the error to screen readers), leading to silent UI failures and severe accessibility gaps when backend APIs return 500s.
**Action:** When implementing `fetch` chains, ALWAYS check `!response.ok` and explicitly `throw new Error()`. If handling errors locally with `.catch()`, ensure you re-throw the error so parent calling functions are aware of the failure state.
## 2024-05-19 - Avoid Inline Styles for Component Micro-Interactions
**Learning:** Even minor component interactions, like `<kbd>` hover states for tooltips, shouldn't be patched with inline `<style>` blocks in HTML5. Although functionally valid, doing so breaks separation of concerns, complicates maintainability, and ignores existing style hierarchies.
**Action:** Always map hover and focus-visible states into the central stylesheet (e.g., `glass.css`), ensuring consistency and cleaner HTML.

## 2026-05-18 - Semantic Class Toggling for JS Micro-Interactions
**Learning:** Directly mutating inline `style` properties via JavaScript (e.g., `element.style.transform = 'scale(0.85)'`) to simulate tactile feedback (like keypresses) tightly couples logic to presentation, violates separation of concerns, and creates unmaintainable inline styles.
**Action:** When implementing JS-driven micro-interactions, always toggle semantic CSS classes (e.g., `classList.add('kbd-active')`) and map the visual transition states into the central stylesheet.
## 2026-05-08 - Revert Optimistic UI Updates on Error
**Learning:** When async state changes fail in SPAs, the optimistic UI update (like a select dropdown value changing immediately) causes a state mismatch with the displayed data if not reverted.
**Action:** Immediately revert optimistic UI updates (like select dropdown values) back to their previous state in the `.catch()` block of async operations to prevent misleading visual mismatches between the active control element and the currently displayed data.

## 2026-05-10 - Focus Loss on Natively Disabled Controls
**Learning:** Using the native `disabled` property on form controls (like `<select>` or `<button>`) during asynchronous operations drops keyboard focus entirely, placing users back at the top of the document or requiring them to tab through the interface again. This breaks the expected navigation flow for keyboard and screen reader users.
**Action:** Instead of disabling elements natively during loading states, use `aria-disabled="true"` to announce the state to screen readers, while relying on custom CSS (e.g., matching the visual disabled style and adding `pointer-events: none`) and early-return JS logic to prevent interactions. This keeps the element focusable and preserves user context.

## 2026-05-13 - Focus/Hover Loss on Disabled Controls Using pointer-events
**Learning:** When disabling form controls (like `<select>` or `<button>`) during asynchronous operations, avoiding the native `disabled` property in favor of `aria-disabled="true"` is correct for preserving keyboard focus. However, if the accompanying CSS applies `pointer-events: none;`, it entirely suppresses all mouse interaction state, meaning native tooltips (like the `title` attribute) and custom cursors (like `cursor: wait`) will not appear, hiding vital visual feedback.
**Action:** Do NOT apply `pointer-events: none` in CSS to `aria-disabled="true"` elements if you rely on `title` or `cursor` feedback. Instead, explicitly handle interaction prevention via JavaScript (e.g., calling `e.preventDefault()` and `e.stopPropagation()` in capturing `click` and `mousedown` event listeners for elements with `aria-disabled="true"`).
## 2024-05-15 - Add tactile visual feedback to interactive controls
**Learning:** Adding an `:active` state with a subtle scale transform (`scale(0.95)`) provides important tactile feedback on buttons and selects, making the UI feel responsive, especially on touch devices or when there's a slight delay before an action takes place. It's crucial to guard this with `:not(:disabled):not([aria-disabled="true"])` to prevent false affordances on disabled elements.
**Action:** When implementing interactive elements like buttons or custom dropdowns, always consider the complete interaction lifecycle: hover, focus-visible, and active.
## 2025-02-20 - Interactive Element Cues and State Discoverability
**Learning:** Adding a crosshair cursor to empty/blank interactive charting areas significantly clarifies that the space is reactive, and linking keyboard shortcut badges to their associated form control's focus state using CSS `:has()` drastically improves shortcut discoverability for keyboard-only users.
**Action:** When creating empty data visualization spaces or pairing labels with keyboard shortcuts, always provide a pointer affordance (like `crosshair`) and dynamically highlight the shortcut badge when its associated input receives focus.

## 2026-05-19 - Dynamic DOM Reordering for SVG Hover Affordances
**Learning:** In dense SVG visualizations (like vector fields or phase portraits), a CSS `:hover` effect that increases stroke width can be completely obscured by overlapping sibling elements that were drawn later in the DOM order. Because SVG does not support `z-index`, the visual affordance is lost.
**Action:** When implementing hover affordances on dense SVG elements (like lines or circles), bind a JS event listener (e.g., `d3.select(this).raise()` on `mouseenter`) to dynamically reorder the DOM and bring the hovered element to the front, ensuring the CSS styles are fully visible.

## 2026-05-20 - Chart Accessibility for Colorblind Users
**Learning:** In data visualizations like line charts, relying solely on hue differences (color) to distinguish between multiple datasets (e.g., state variables x1, x2, x3) makes the chart inaccessible to users with color vision deficiencies. Without structural differences, the lines can blend together or become indistinguishable.
**Action:** When plotting multiple lines on a single chart, always incorporate structural visual differences, such as distinct dashed or dotted patterns (e.g., using `borderDash` in Chart.js), in addition to color, to ensure all users can differentiate the data series.
## 2025-02-23 - App Polish & Integration
**Learning:** Adding a basic SVG data-uri favicon and theme-color meta tag instantly integrates a web application with browser UIs (tab icons, mobile toolbars) and clears standard console 404 warnings without requiring an image editor or heavy assets.
**Action:** Always include a lightweight data-uri SVG favicon and a `theme-color` meta tag in foundational `index.html` headers for instant visual polish and cleaner console outputs.

## 2026-05-24 - False Hover Affordance on aria-disabled Elements
**Learning:** When form controls use `aria-disabled="true"` instead of native `:disabled` to preserve keyboard focus during async operations, standard CSS hover pseudo-classes (e.g., `button:hover:not(:disabled)`) will still trigger. This provides users with a false interactive affordance, making it look like a disabled element can be clicked.
**Action:** When creating hover styles for interactive elements, always explicitly negate the `aria-disabled` attribute (e.g., `:not([aria-disabled="true"])`) alongside the native `:disabled` pseudo-class to prevent misleading hover states.

## 2026-05-25 - Preventing Native Shortcut Hijacking
**Learning:** When implementing custom global single-character keyboard shortcuts (like pressing "S" to focus a search bar or select dropdown), always ensure you check and ignore events where modifier keys (`Ctrl`, `Meta`, `Alt`) are active. Failing to explicitly ignore these keys means that standard native browser shortcuts (like `Ctrl+S` / `Cmd+S` to save the page, or `Cmd+R` / `Ctrl+R` to reload) will be violently hijacked and suppressed by `e.preventDefault()`, leading to severe user frustration and breaking established mental models.
**Action:** In `keydown` event listeners intended for single-character shortcuts, inject an early return condition like `if (e.ctrlKey || e.metaKey || e.altKey) return;` before checking the `e.key` value and calling `e.preventDefault()`.

## 2026-05-26 - Domain-Specific Contextual Labels in Visualizations
**Learning:** Using generic variable names (like 'x1', 'x2' or 'theta') in data visualizations (tooltips, legends, axes) increases cognitive load for users when they are analyzing domain-specific models (like physical pendulums or specific attractors). Users expect typography to match established mathematical conventions (e.g., θ, ω) across all interactive components to maintain a seamless analytical experience.
**Action:** When rendering multi-domain mathematical visualizations, ensure state variables map to domain-specific Unicode characters consistently across all interface layers (chart legends, axis labels, and SVG tooltips).

## 2026-05-27 - Limitations of title for Interaction Affordances
**Learning:** For interactive canvas elements (like a 3D view) that pause on focus/hover, using a `title` attribute communicates the affordance to sighted users but is often ignored by screen readers on non-form elements. This leaves assistive technology users unaware of how to control the animation.
**Action:** When implementing interactive affordances on complex visualization containers, explicitly append the interaction instructions (e.g., "Focus to pause animation.") directly to the container's `aria-label`.

## 2026-05-28 - Macro-Level Spatial Context with focus-within
**Learning:** Keyboard users navigating through dense dashboards can easily lose spatial context of which major section (landmark) they are currently interacting with, especially when focus moves deep within a complex component like a chart or 3D view.
**Action:** Apply `:focus-within` styles (such as subtle border-color changes and box-shadow glows) to the parent layout containers (e.g., `.glass-panel`) to provide a persistent, macro-level visual anchor indicating the active region.

## 2026-05-30 - OS-Level Native Dark Theme Fallbacks
**Learning:** Setting a dark CSS background color (`background-color: #0f172a`) on an application does not automatically inform the browser or OS that the application is operating in a "dark mode". As a result, native browser components (like default scrollbars, `<select>` dropdown menus, and context menus) will render in their glaring white default state, breaking immersion and causing potentially jarring visual flashes.
**Action:** Always include `color-scheme: dark;` (or `dark light` if supporting both) in the `:root` pseudo-class for dark-themed web applications to ensure native OS UI components seamlessly inherit the dark visual context.

## 2026-05-30 - Fallback for JS-Heavy Applications
**Learning:** For web applications that are fundamentally un-renderable without JavaScript (like those relying exclusively on client-side WebGL or Canvas rendering), users with JS disabled (or certain web crawlers/assistive tech) will encounter a confusing, completely blank page with no indication of why it failed to load.
**Action:** Always include a prominently styled `<noscript>` block immediately inside the `<body>` tag for JS-heavy applications to provide a polite, explicitly clear warning that JavaScript is required for the application to function.

## 2026-06-04 - Invisible Tactile Feedback for Programmatic Focus
**Learning:** When using JavaScript `.focus()` to programmatically focus a button (e.g., as part of a global keyboard shortcut), modern browsers typically do not trigger the `:focus-visible` CSS pseudo-class, as they attempt to differentiate between keyboard navigation and script-driven focus. If a tooltip or shortcut badge relies on `:focus-visible` (e.g., `opacity: 1`) to appear, it will remain invisible during the shortcut activation.
**Action:** If you use a `.kbd-active` class to trigger an active state animation for tactile feedback when a shortcut is pressed, explicitly include `opacity: 1 !important` (or the equivalent visibility property) in the `.kbd-active` class itself to ensure the badge appears regardless of whether `:focus-visible` triggers.

## 2026-06-05 - Interaction Modality Collisions (Hover vs Focus)
**Learning:** When manually tracking multiple input modalities (mouse hover, keyboard focus, touch) for a single interaction state (like pausing a 3D animation) using a single, shared boolean flag, destructive state collisions occur. For instance, if a user focuses an element with the keyboard and then moves their mouse across it, the `mouseleave` event will blindly toggle the flag to false, violently un-pausing the animation and breaking the keyboard-user's expected visual contract.
**Action:** When an interactive state responds to multiple event modalities, decouple the underlying state trackers into discrete boolean variables (e.g., `isHovered`, `isFocused`, `isTouched`). Compute the final visible state dynamically (e.g., `isHovered || isFocused || isTouched`) so that exiting one modality does not inadvertently destroy the state of another active modality.
## 2024-05-09 - Hardcoding aria-live regions for initial announcement reliability
**Learning:** Programmatically generating and appending an `aria-live` element during the `DOMContentLoaded` event often causes screen readers (like VoiceOver) to miss the very first announcement (e.g., initial loading states). Screen readers build their accessibility tree on page parse, and late additions of live regions are not always reliably registered to announce immediate text content changes.
**Action:** Always hardcode structural `aria-live` announcer regions directly into the static HTML `<body>` to ensure they are present in the DOM before any JavaScript attempts to update their `textContent`.

## 2026-06-08 - Visual Feedback Sync for Multi-Modal Interactions
**Learning:** When interactive elements handle multiple modalities (hover, focus, touch) and track them with JS to determine an active state (like `isPausedByUser`), relying on pure CSS pseudo-classes (`:hover`, `:focus-visible`) for visual feedback leads to mismatched states. For example, a touch event on a mobile device may trigger the JS pause logic but fail to trigger the CSS `:hover` or `:focus-visible` pseudo-class, rendering the element paused but without the visual "Paused" indicator.
**Action:** Always sync visual feedback classes (e.g., adding `.is-paused` via JS) directly to the logical interaction state rather than relying on CSS pseudo-classes when dealing with custom multi-modal input handling.

## 2026-06-10 - SPA Bookmarkability via URL Hash Syncing
**Learning:** Single Page Applications (SPAs) that heavily rely on client-side rendering can frustrate users if the URL does not update to reflect their current configuration. Without syncing primary state variables to the URL, users lose the ability to bookmark specific views or share them easily with colleagues, which is a major UX regression compared to traditional multi-page navigation.
**Action:** When implementing primary view controllers (like a top-level system model selector), always ensure the current configuration state is synced to the URL hash (e.g., using `window.history.replaceState`), and ensure the application can read that hash on initial load to restore the user's context seamlessly.

## 2026-06-11 - Sticky Hovers and Keyboard Hints on Touch Devices
**Learning:** On iOS and Android devices, CSS `:hover` states can become "sticky" after a user taps an element. Because touch devices lack a true hover state, tapping an element triggers both active and hover styles, but the hover style often remains persistently applied even after the touch is released. Furthermore, displaying keyboard shortcuts (e.g., `[S]`) on mobile devices adds useless visual clutter since physical keyboards are rarely used.
**Action:** Always wrap interactive `:hover` state declarations (like button backgrounds or vector line strokes) in `@media (hover: hover)` to ensure they only trigger on devices capable of genuine pointer hover. Additionally, use `@media (pointer: coarse)` to apply `display: none !important` to `.kbd-shortcut` hint elements, hiding irrelevant keyboard information from mobile users.

## 2026-06-12 - Explicit Affordances for SPA Sharing
**Learning:** While automatically syncing Single Page Application (SPA) configuration state to the URL hash (e.g., `#VanDerPol`) is excellent for bookmarkability, relying on users to manually copy the URL from their browser's address bar suffers from poor discoverability. Many users, especially on mobile or within embedded web-views, may not realize the URL has updated or may find it difficult to copy.
**Action:** When implementing URL hash syncing for shareable views, always provide an explicit, accessible UI affordance (like a "Copy Link" button with an icon and `aria-label`) to reduce friction and clearly communicate that the current state is shareable. Ensure the button provides tactile visual feedback (e.g., swapping to a checkmark) and auditory feedback via `aria-live` regions upon success.

## 2026-06-13 - Syncing Transient Visual States with Accessibility Semantics
**Learning:** When displaying temporary visual success states (like turning a "Copy Link" icon into a green checkmark for 2 seconds), leaving the original `title` and `aria-label` (e.g., "Copy link to current state") unchanged creates severe cognitive dissonance. Sighted users hovering over the checkmark see a tooltip telling them to "Copy link" even though it just succeeded, and screen reader users navigating back to the button during the animation hear the original action prompt instead of the success confirmation.
**Action:** Always explicitly sync transient visual interaction states with their corresponding accessibility attributes. When injecting temporary success HTML, simultaneously update `title` and `aria-label` to match the new visual semantics (e.g., "Copied!"), and ensure they are reliably reverted when the visual state resets.

## 2026-06-14 - Transient State Corruption on Rapid Interaction
**Learning:** When temporarily replacing a button's `innerHTML` to show a transient success state (like a checkmark), storing the original HTML inside the click event listener causes state corruption if the user clicks rapidly before the timeout resets. The "original" HTML becomes the temporary checkmark, permanently breaking the UI.
**Action:** Always cache the original state variables (`innerHTML`, `title`, etc.) outside the event listener. Additionally, apply `aria-disabled="true"` during the transient state to prevent spam clicks and protect the interaction cycle.

## 2026-06-15 - Decoupling Success States from Disabled Styles
**Learning:** When using `aria-disabled="true"` as an interaction guard to prevent double-clicks during a transient success animation (like a checkmark), the element inadvertently inherits generic disabled styles (e.g., `opacity: 0.5`, `cursor: wait`). This dims the success indicator and provides confusing cursor feedback, breaking the positive confirmation experience.
**Action:** When applying an interaction guard for a success state, apply a distinct modifier class (e.g., `.is-success`) to explicitly override the generic disabled opacity and cursor, ensuring the success visual remains vibrant and clear.

## 2026-06-16 - Auditory Feedback for Implicit State Changes
**Learning:** When an element implicitly changes system state purely by receiving focus, hover, or touch (such as pausing an animation), sighted users might receive feedback via visual indicators (like a paused badge). However, screen reader users do not receive auditory confirmation because these visual indicators are often marked with `aria-hidden="true"` to prevent screen readers from reading them constantly as they navigate.
**Action:** Always explicitly announce implicit state changes via an `aria-live` region to provide feedback parity for screen reader users when visual indicators are inaccessible. Keep track of the previous state to ensure we only announce when the state actually *changes*, rather than on every continuous interaction event.
