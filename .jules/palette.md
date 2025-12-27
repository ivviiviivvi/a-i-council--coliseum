## 2024-05-23 - "Skip to content" in modern frameworks
**Learning:** Even with component-based frameworks like Next.js where navigation might not be in the initial DOM (or strictly separated), adding a "Skip to content" link is a fundamental accessibility pattern that's often overlooked. It's surprisingly easy to implement with Tailwind's `sr-only` and `focus:not-sr-only` utilities, making it invisible until needed.
**Action:** Always check `layout.tsx` (or equivalent root) for this link as the very first accessibility check.
