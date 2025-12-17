## 2024-05-22 - [Accessibility & Focus States]
**Learning:** Screen readers announce decorative emojis in headings (e.g., "Robot Face AI Agents") which adds noise. Wrapping them in `<span aria-hidden="true">` solves this cleanly.
**Learning:** Tailwind's default buttons often lack visible focus states. Adding `focus-visible:ring-2` is essential for keyboard navigation and meets accessibility standards.
**Action:** Always check heading content for decorative elements and wrap them. Ensure all interactive elements have explicit focus styles defined in `globals.css` or component classes.
