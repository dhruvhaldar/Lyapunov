# Palette's Journal

## 2024-03-24 - Accessibility Insights
**Learning:** Found an opportunity to improve accessibility on the `Lyapunov` project. Many interactive UI elements like `select` and `button` lack appropriate ARIA labels or `title` attributes to assist screen readers. Also, elements lack proper `aria-label` or `title` to provide more context about what system is being selected or what button is being pressed.
**Action:** Consistently add `aria-label` and `title` to select fields and buttons. Also add roles to non-standard interactive elements if any.