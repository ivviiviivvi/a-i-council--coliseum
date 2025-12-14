## 2024-05-23 - Focus States for Accessibility
**Learning:** Custom buttons using `@apply` in Tailwind often miss default browser focus states because of `focus:outline-none` or just because custom styles override defaults. Explicitly adding `focus-visible` states is crucial for keyboard navigation.
**Action:** Always check interactive elements for `focus-visible` styles when reviewing or creating new components. Use a consistent focus ring color and offset to ensure visibility on all backgrounds.
