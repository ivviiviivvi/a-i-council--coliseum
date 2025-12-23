# Palette's Journal

This journal tracks critical UX/accessibility learnings and reusable patterns.

## 2024-05-22 - Focus Visibility and Tactile Feedback
**Learning:** Default browser focus rings are often obscured by custom button styles or simply look out of place, leading to poor keyboard accessibility. Users also appreciate tactile feedback (active states) on interactive elements.
**Action:** Consistently apply `focus-visible` styles using `ring` utilities in Tailwind and `active:scale-95` for button presses in the design system components.
