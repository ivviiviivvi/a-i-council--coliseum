## 2024-05-24 - Focus States on Custom Buttons
**Learning:** Custom utility classes defined in `globals.css` via `@apply` often miss `focus-visible` states, making keyboard navigation difficult. The default browser focus ring can be hidden by `outline-none` or clash with the design.
**Action:** When creating custom button classes (e.g., `.btn-primary`), always explicitly include `focus-visible:ring` styles to ensure accessible and consistent keyboard navigation.
