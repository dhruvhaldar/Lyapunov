1. **Update `public/index.html`**:
   - Replace the `title` attribute with `data-tooltip` on `#refresh-btn` and `#copy-link-btn`.
2. **Update `public/js/main.js`**:
   - Change references of `title` (using `getAttribute`, `setAttribute`, or `.title`) for `#refresh-btn` and `#copy-link-btn` to use `data-tooltip` instead.
3. **Update `public/css/glass.css`**:
   - Add CSS pseudo-element (`::after`) styling for `[data-tooltip]` elements.
   - Configure the tooltips to appear on `:hover` and `:focus-visible` with a smooth transition, positioned above the icon buttons to not overlap with existing keyboard hint UI elements.
4. **Complete pre-commit steps**:
   - Run tests (e.g. `python3 -m pytest tests/`) to ensure no regressions are introduced.
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
5. **Submit**:
   - Submit the changes using the commit message format required for Palette.
