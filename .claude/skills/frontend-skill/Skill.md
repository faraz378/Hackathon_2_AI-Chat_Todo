---
name: frontend-skill
description: Build user interfaces by creating pages, reusable components, layouts, and applying modern styling practices.
---

# Frontend Development

## Instructions

1. **Page Construction**
   - Build route-based pages
   - Structure content semantically
   - Handle loading and error states
   - Optimize for SEO and accessibility

2. **Component Design**
   - Create reusable, composable components
   - Follow single-responsibility principle
   - Accept props and manage state cleanly
   - Separate logic from presentation

3. **Layout System**
   - Use responsive grid or flex layouts
   - Implement shared layouts (header, footer, sidebar)
   - Support nested and dynamic layouts
   - Ensure consistency across pages

4. **Styling**
   - Apply modern CSS practices
   - Use utility-first or component-based styling
   - Maintain design tokens (spacing, colors, typography)
   - Support dark mode and theming

5. **Interactivity**
   - Handle user events
   - Manage client-side state
   - Animate transitions responsibly
   - Optimize rendering performance

## Best Practices
- Mobile-first responsive design
- Keep components small and reusable
- Avoid deeply nested components
- Use semantic HTML elements
- Ensure accessibility (ARIA, keyboard support)
- Optimize for performance and bundle size

## Example Structure

### Page Layout
```tsx
<Layout>
  <Header />
  <MainContent>
    <PageTitle />
    <Section />
  </MainContent>
  <Footer />
</Layout>

<Card>
  <CardHeader title="Title" />
  <CardContent>
    Content goes here
  </CardContent>
</Card>
