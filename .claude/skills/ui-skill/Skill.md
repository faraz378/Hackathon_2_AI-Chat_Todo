---
name: ui-update-skill
description: Update and refine existing user interfaces by modifying components, layouts, and styles without breaking functionality.
---

# UI Update & Refinement

## Instructions

1. **UI Analysis**
   - Review existing pages and components
   - Identify outdated or inconsistent UI elements
   - Detect spacing, alignment, and typography issues
   - Ensure no functional regressions

2. **Component Updates**
   - Modify existing components only (no rewrites unless required)
   - Improve visual hierarchy and clarity
   - Refactor styles for consistency
   - Preserve component APIs and behavior

3. **Layout Adjustments**
   - Fix alignment and spacing issues
   - Improve responsive behavior
   - Update shared layouts if needed
   - Maintain design consistency across screens

4. **Styling Improvements**
   - Update colors, typography, and spacing
   - Align UI with design system or brand guidelines
   - Improve contrast and readability
   - Support light/dark mode if applicable

5. **UX Enhancements**
   - Improve button states and feedback
   - Refine hover, focus, and active states
   - Smooth transitions and micro-interactions
   - Enhance accessibility (ARIA, keyboard navigation)

## Best Practices
- Do not change business logic
- Avoid breaking existing layouts
- Make incremental, reversible changes
- Test UI across screen sizes
- Prioritize usability and clarity
- Follow accessibility standards (WCAG)

## Example Structure

### Before → After Update
```tsx
<Button className="px-2 py-1 text-sm">
  Save
</Button>

<Button className="px-4 py-2 text-sm font-medium rounded-lg">
  Save Changes
</Button>
