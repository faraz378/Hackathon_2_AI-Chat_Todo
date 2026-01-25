# Quickstart Guide: Frontend & Integration

**Feature**: 003-frontend-integration
**Date**: 2026-01-13
**Purpose**: Setup instructions, development workflow, and testing guide for the Next.js frontend

---

## Prerequisites

Before starting, ensure you have:

1. **Backend Running**: The FastAPI backend from Spec-1 and Spec-2 must be running
   - Backend should be accessible at `http://localhost:8000`
   - Database migrations applied (user authentication tables exist)
   - CORS configured to allow requests from `http://localhost:3000`

2. **Development Environment**:
   - Node.js 18+ installed
   - npm or yarn package manager
   - Modern web browser (Chrome, Firefox, Safari, or Edge)

3. **Backend API Verification**:
   ```bash
   # Test backend is running
   curl http://localhost:8000/

   # Test auth endpoints exist
   curl -X POST http://localhost:8000/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
   ```

---

## Initial Setup

### 1. Create Frontend Directory

```bash
# From repository root
mkdir -p frontend
cd frontend
```

### 2. Initialize Next.js Project

```bash
# Create Next.js app with TypeScript and Tailwind
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir

# Answer prompts:
# ✔ Would you like to use ESLint? Yes
# ✔ Would you like to use Turbopack? No
# ✔ Would you like to customize the default import alias? No
```

### 3. Install Dependencies

```bash
# Core dependencies
npm install zod

# Development dependencies
npm install --save-dev @types/node @types/react @types/react-dom

# Testing dependencies
npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install --save-dev @playwright/test
```

### 4. Configure Environment Variables

Create `.env.local` file in `frontend/` directory:

```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Create `.env.local.example` for documentation:

```bash
# .env.local.example
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Add to `.gitignore`:

```bash
# Add to frontend/.gitignore
.env.local
```

### 5. Configure TypeScript

Update `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### 6. Configure Tailwind CSS

Update `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
      },
    },
  },
  plugins: [],
}
```

---

## Development Workflow

### Start Development Server

```bash
# From frontend/ directory
npm run dev

# Server starts at http://localhost:3000
```

### Project Structure Setup

Create the directory structure:

```bash
# From frontend/ directory
mkdir -p src/app/{signup,signin,dashboard}
mkdir -p src/components/{auth,tasks,layout,ui}
mkdir -p src/lib/{api,auth,validation}
mkdir -p src/types
mkdir -p tests/{components,e2e}
```

### Development Order

Follow this order for implementation (matches tasks.md):

1. **Phase 1: Core Infrastructure**
   - API client with JWT injection (`lib/api/client.ts`)
   - Auth context and hooks (`lib/auth/context.tsx`, `lib/auth/hooks.ts`)
   - Token storage utilities (`lib/auth/storage.ts`)
   - TypeScript types (`types/`)

2. **Phase 2: Authentication UI**
   - Signup page (`app/signup/page.tsx`)
   - Signin page (`app/signin/page.tsx`)
   - Auth forms (`components/auth/`)
   - Form validation schemas (`lib/validation/schemas.ts`)

3. **Phase 3: Task Management UI**
   - Dashboard page (`app/dashboard/page.tsx`)
   - Task list component (`components/tasks/TaskList.tsx`)
   - Task item component (`components/tasks/TaskItem.tsx`)
   - Task form component (`components/tasks/TaskForm.tsx`)
   - Empty state component (`components/tasks/EmptyState.tsx`)

4. **Phase 4: Layout & Navigation**
   - Root layout with auth provider (`app/layout.tsx`)
   - Header with navigation (`components/layout/Header.tsx`)
   - Protected route wrapper (`components/auth/ProtectedRoute.tsx`)

5. **Phase 5: UI Components**
   - Button component (`components/ui/Button.tsx`)
   - Input component (`components/ui/Input.tsx`)
   - Loading spinner (`components/ui/LoadingSpinner.tsx`)
   - Error message (`components/ui/ErrorMessage.tsx`)

6. **Phase 6: Testing**
   - Component tests
   - E2E tests

---

## Testing Guide

### Manual Testing Scenarios

#### Scenario 1: User Registration Flow

1. **Start backend and frontend**:
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn src.main:app --reload --port 8000

   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

2. **Test signup**:
   - Navigate to `http://localhost:3000/signup`
   - Enter email: `testuser@example.com`
   - Enter password: `password123`
   - Click "Sign Up"
   - **Expected**: Redirected to dashboard, see empty state

3. **Verify token storage**:
   - Open browser DevTools → Application → Local Storage
   - **Expected**: See `auth_token` key with JWT value

#### Scenario 2: User Sign In Flow

1. **Test signin**:
   - Navigate to `http://localhost:3000/signin`
   - Enter email: `testuser@example.com`
   - Enter password: `password123`
   - Click "Sign In"
   - **Expected**: Redirected to dashboard

2. **Test invalid credentials**:
   - Navigate to `http://localhost:3000/signin`
   - Enter email: `testuser@example.com`
   - Enter password: `wrongpassword`
   - Click "Sign In"
   - **Expected**: Error message "Invalid email or password"

#### Scenario 3: Task Management Flow

1. **Create task**:
   - Sign in and navigate to dashboard
   - Click "Create Task" button
   - Enter title: "Buy groceries"
   - Enter description: "Milk, eggs, bread"
   - Click "Save"
   - **Expected**: Task appears in list immediately

2. **Edit task**:
   - Click "Edit" on the task
   - Change title to "Buy groceries and fruits"
   - Click "Save"
   - **Expected**: Task updates in list

3. **Complete task**:
   - Click checkbox on task
   - **Expected**: Task shows strikethrough, checkmark appears

4. **Delete task**:
   - Click "Delete" on task
   - Confirm deletion
   - **Expected**: Task removed from list

#### Scenario 4: Protected Routes

1. **Test unauthenticated access**:
   - Sign out (or clear localStorage)
   - Navigate to `http://localhost:3000/dashboard`
   - **Expected**: Redirected to `/signin`

2. **Test authenticated access**:
   - Sign in
   - Navigate to `http://localhost:3000/dashboard`
   - **Expected**: Dashboard loads with tasks

#### Scenario 5: Token Expiration

1. **Simulate expired token**:
   - Sign in
   - Open DevTools → Application → Local Storage
   - Manually edit `auth_token` to invalid value
   - Try to create a task
   - **Expected**: Redirected to `/signin` with "Session expired" message

#### Scenario 6: Multi-User Isolation

1. **Create two users**:
   - Sign up as `user1@example.com`
   - Create tasks: "User 1 Task A", "User 1 Task B"
   - Sign out

2. **Sign in as second user**:
   - Sign up as `user2@example.com`
   - Create tasks: "User 2 Task A", "User 2 Task B"

3. **Verify isolation**:
   - **Expected**: User 2 only sees their own tasks
   - Sign out and sign in as User 1
   - **Expected**: User 1 only sees their own tasks

#### Scenario 7: Responsive Design

1. **Test mobile viewport**:
   - Open DevTools → Toggle device toolbar
   - Select iPhone SE (375px width)
   - Navigate through all pages
   - **Expected**: Layout adapts, all buttons accessible

2. **Test tablet viewport**:
   - Select iPad (768px width)
   - **Expected**: Layout uses tablet breakpoints

3. **Test desktop viewport**:
   - Select Responsive, set to 1920px width
   - **Expected**: Layout uses desktop breakpoints, content centered

#### Scenario 8: Error Handling

1. **Test network error**:
   - Stop backend server
   - Try to create a task
   - **Expected**: Error message "Unable to connect to server"

2. **Test validation error**:
   - Try to create task with empty title
   - **Expected**: Error message "Title is required"

3. **Test duplicate email**:
   - Try to sign up with existing email
   - **Expected**: Error message "This email is already registered"

---

## Automated Testing

### Unit/Component Tests (Jest + React Testing Library)

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

**Example test file** (`tests/components/TaskItem.test.tsx`):

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import TaskItem from '@/components/tasks/TaskItem';

describe('TaskItem', () => {
  const mockTask = {
    id: 1,
    title: 'Test Task',
    description: 'Test Description',
    completed: false,
    user_id: 1,
    created_at: '2026-01-13T10:00:00Z',
    updated_at: '2026-01-13T10:00:00Z',
  };

  it('renders task title and description', () => {
    render(<TaskItem task={mockTask} onUpdate={jest.fn()} onDelete={jest.fn()} />);
    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  it('calls onUpdate when checkbox clicked', () => {
    const onUpdate = jest.fn();
    render(<TaskItem task={mockTask} onUpdate={onUpdate} onDelete={jest.fn()} />);

    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);

    expect(onUpdate).toHaveBeenCalledWith(1, { completed: true });
  });
});
```

### End-to-End Tests (Playwright)

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run E2E tests
npm run test:e2e

# Run E2E tests in UI mode
npx playwright test --ui
```

**Example E2E test** (`tests/e2e/auth-flow.spec.ts`):

```typescript
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('user can sign up, sign in, and access dashboard', async ({ page }) => {
    // Sign up
    await page.goto('http://localhost:3000/signup');
    await page.fill('input[name="email"]', 'e2e@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/);

    // Sign out
    await page.click('button:has-text("Sign Out")');

    // Should redirect to signin
    await expect(page).toHaveURL(/.*signin/);

    // Sign in
    await page.fill('input[name="email"]', 'e2e@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Should be back on dashboard
    await expect(page).toHaveURL(/.*dashboard/);
  });
});
```

---

## Troubleshooting

### Issue: CORS Error

**Symptom**: Browser console shows "CORS policy" error

**Solution**: Ensure backend has CORS configured:

```python
# backend/src/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Token Not Persisting

**Symptom**: User logged out after page refresh

**Solution**: Check localStorage in DevTools. Ensure token is being saved:

```typescript
// lib/auth/storage.ts should have:
localStorage.setItem('auth_token', token);
```

### Issue: 401 Unauthorized on All Requests

**Symptom**: All API requests return 401

**Solution**: Check Authorization header is being sent:

```typescript
// lib/api/client.ts should include:
headers: {
  'Authorization': `Bearer ${token}`,
}
```

### Issue: Next.js Build Errors

**Symptom**: `npm run build` fails

**Solution**: Check for:
- Missing "use client" directives on components using hooks
- Server Components trying to use browser APIs
- Missing environment variables

### Issue: Hydration Errors

**Symptom**: Console shows "Hydration failed" error

**Solution**: Ensure:
- Server and client render the same HTML
- No browser-only code in Server Components
- localStorage access wrapped in useEffect

---

## Performance Optimization

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

### Lighthouse Audit

```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run audit
lighthouse http://localhost:3000 --view
```

**Target Scores**:
- Performance: > 90
- Accessibility: > 90
- Best Practices: > 90
- SEO: > 90

---

## Deployment Checklist

Before deploying to production:

- [ ] All tests passing (`npm test` and `npm run test:e2e`)
- [ ] Production build succeeds (`npm run build`)
- [ ] Environment variables configured for production
- [ ] Backend API URL updated in `.env.production`
- [ ] CORS configured for production domain
- [ ] Lighthouse scores meet targets
- [ ] Manual testing completed on production build
- [ ] Multi-user isolation verified
- [ ] Token expiration handling tested
- [ ] Responsive design verified on real devices

---

## Next Steps

After completing the frontend implementation:

1. **Integration Testing**: Test full-stack flow with real backend
2. **User Acceptance Testing**: Have stakeholders test the application
3. **Performance Tuning**: Optimize based on Lighthouse audit
4. **Documentation**: Update README with deployment instructions
5. **Demo Preparation**: Prepare hackathon demonstration script

---

## Support

For issues or questions:
- Check backend logs: `backend/logs/`
- Check browser console for frontend errors
- Verify API contracts match between frontend and backend
- Review Spec-1 and Spec-2 documentation
