## 2026-03-27 - Added Loading State to Action Buttons
**Learning:** Adding explicit loading states (disabled button + text change) to asynchronous fetch operations prevents user frustration, duplicate submissions, and clearly signals that an action is currently in progress, particularly for potentially slow math-heavy backend endpoints.
**Action:** Always wrap `fetch` calls with immediate UI updates that disable submit/action buttons, change the label to indicate progress (e.g., "Updating...", "Simulating..."), and use a `.finally()` block to ensure the button is re-enabled and restored to its original text regardless of request success or failure. Also ensure CSS supports the disabled state visually.

## 2026-03-27 - Global Controls and Auto-Synchronization
**Learning:** Placing a global control (like a system selector) inside a single localized component panel breaks the Law of Proximity and confuses users about the control's scope. Requiring manual button clicks for each individual visualization panel after changing a global setting introduces significant friction.
**Action:** Always elevate global state controls to global UI containers (like the page header). Bind these controls to `change` events that automatically synchronize and update all dependent visual components simultaneously to create a cohesive, frictionless experience without unnecessary click paths.

## 2026-03-30 - Coordinating Async State & Screen Reader Announcements
**Learning:** When multiple visualizations update automatically in response to a single global state change (e.g., changing a dropdown), independent async requests can lead to race conditions or confused screen reader users. Simply disabling a control isn't enough; blind users need to know *why* it's disabled and when it finishes.
**Action:** Ensure all async UI update functions return their underlying `Promise`. In the global event listener, disable the trigger control, inject a polite `aria-live` announcement (e.g., "Loading..."), and use `Promise.all()` to wait for all downstream updates to resolve before re-enabling the control and announcing completion or error states to screen readers.

## 2026-03-31 - Making Custom Data Visualizations Accessible via Keyboard
**Learning:** Adding `role="img"` and `aria-label` to custom data visualizations (like `<canvas>` or `<div>` containers drawing charts/3D scenes) is good for screen readers, but if the elements are purely visual containers, they are not naturally in the keyboard tab order. To make them fully accessible, they must also have `tabindex="0"` and a visible `:focus-visible` styling. Without these, keyboard users cannot navigate to them to have their `aria-label`s announced.
**Action:** When adding `role="img"` to custom interactive data visualization containers (`<div>`, `<canvas>`), always pair it with `tabindex="0"` and ensure your CSS includes `[role="img"][tabindex="0"]:focus-visible` styling so they are discoverable and focusable.
