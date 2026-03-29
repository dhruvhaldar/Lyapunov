## 2026-03-27 - Added Loading State to Action Buttons
**Learning:** Adding explicit loading states (disabled button + text change) to asynchronous fetch operations prevents user frustration, duplicate submissions, and clearly signals that an action is currently in progress, particularly for potentially slow math-heavy backend endpoints.
**Action:** Always wrap `fetch` calls with immediate UI updates that disable submit/action buttons, change the label to indicate progress (e.g., "Updating...", "Simulating..."), and use a `.finally()` block to ensure the button is re-enabled and restored to its original text regardless of request success or failure. Also ensure CSS supports the disabled state visually.

## 2026-03-27 - Global Controls and Auto-Synchronization
**Learning:** Placing a global control (like a system selector) inside a single localized component panel breaks the Law of Proximity and confuses users about the control's scope. Requiring manual button clicks for each individual visualization panel after changing a global setting introduces significant friction.
**Action:** Always elevate global state controls to global UI containers (like the page header). Bind these controls to `change` events that automatically synchronize and update all dependent visual components simultaneously to create a cohesive, frictionless experience without unnecessary click paths.
