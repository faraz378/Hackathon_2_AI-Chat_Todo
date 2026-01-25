# Integration Test Plan - Todo App MVP

**Date:** 2026-01-13
**Frontend:** http://localhost:3001
**Backend:** http://localhost:8000
**Status:** Ready for Testing

---

## Prerequisites

✅ Backend running on port 8000
✅ Frontend running on port 3001
✅ Environment variables configured (.env.local)
✅ Database initialized with schema

---

## Test Suite 1: User Authentication Flow

### Test 1.1: User Signup (New Account)

**Steps:**
1. Open browser to http://localhost:3001
2. Click "Get Started" button on landing page
3. Fill signup form:
   - Email: `testuser1@example.com`
   - Password: `TestPass123!@#` (must meet complexity requirements)
4. Click "Sign Up" button

**Expected Results:**
- ✅ Form validates password requirements (12+ chars, uppercase, lowercase, number, special char)
- ✅ Signup succeeds and automatically signs in
- ✅ Redirects to `/dashboard`
- ✅ Dashboard shows "Welcome, testuser1@example.com!"
- ✅ Empty state displayed: "No tasks yet"

**Failure Scenarios to Test:**
- Weak password (< 12 chars): Should show validation error
- Missing uppercase/lowercase/number/special: Should show specific error
- Invalid email format: Should show "Invalid email format"
- Duplicate email: Should show "Invalid email or password" (generic message to prevent enumeration)

---

### Test 1.2: User Signin (Existing Account)

**Steps:**
1. Click "Sign Out" button in dashboard header
2. Should redirect to `/signin`
3. Fill signin form:
   - Email: `testuser1@example.com`
   - Password: `TestPass123!@#`
4. Click "Sign In" button

**Expected Results:**
- ✅ Signin succeeds
- ✅ Redirects to `/dashboard`
- ✅ User email displayed in header
- ✅ Previous tasks (if any) are loaded

**Failure Scenarios:**
- Wrong password: Should show "Invalid email or password"
- Non-existent email: Should show "Invalid email or password" (same message)
- Empty fields: Should show validation errors

---

### Test 1.3: Protected Route Access

**Steps:**
1. Sign out if signed in
2. Manually navigate to http://localhost:3001/dashboard

**Expected Results:**
- ✅ Immediately redirects to `/signin?redirect=/dashboard`
- ✅ After signing in, redirects back to `/dashboard`

---

### Test 1.4: Session Persistence

**Steps:**
1. Sign in successfully
2. Refresh the page (F5)
3. Close browser tab and reopen http://localhost:3001/dashboard

**Expected Results:**
- ✅ User remains signed in after page refresh
- ✅ User remains signed in after reopening browser (within 24 hours)
- ✅ Dashboard loads without redirect to signin

---

## Test Suite 2: Task Management (CRUD Operations)

### Test 2.1: Create Task

**Steps:**
1. Sign in as `testuser1@example.com`
2. Click "+ Create New Task" button
3. Fill form:
   - Title: `Buy groceries`
   - Description: `Milk, eggs, bread, and coffee`
4. Click "Create Task" button

**Expected Results:**
- ✅ Form closes
- ✅ New task appears in "Active Tasks" section
- ✅ Task shows title and description
- ✅ Task has unchecked checkbox
- ✅ Task has "Edit" and "Delete" buttons
- ✅ Created timestamp displayed

**Validation Tests:**
- Empty title: Should show "Title is required"
- Title > 200 chars: Should show "Title must be 200 characters or less"
- Description > 1000 chars: Should show "Description must be 1000 characters or less"

---

### Test 2.2: Create Multiple Tasks

**Steps:**
1. Create 3 more tasks:
   - Task 2: "Finish project report" / "Complete sections 3-5"
   - Task 3: "Call dentist" / "Schedule cleaning appointment"
   - Task 4: "Exercise" / "30 min cardio"

**Expected Results:**
- ✅ All 4 tasks appear in "Active Tasks" section
- ✅ Tasks ordered by creation time (newest first)
- ✅ Section header shows "Active Tasks (4)"

---

### Test 2.3: Mark Task as Complete

**Steps:**
1. Click checkbox on "Buy groceries" task

**Expected Results:**
- ✅ Task moves to "Completed Tasks" section
- ✅ Title and description have strikethrough styling
- ✅ Checkbox is checked
- ✅ Section headers update: "Active Tasks (3)" and "Completed Tasks (1)"

---

### Test 2.4: Unmark Completed Task

**Steps:**
1. Click checkbox on "Buy groceries" task in Completed section

**Expected Results:**
- ✅ Task moves back to "Active Tasks" section
- ✅ Strikethrough styling removed
- ✅ Checkbox is unchecked
- ✅ Section headers update: "Active Tasks (4)" and "Completed Tasks (0)"

---

### Test 2.5: Edit Task

**Steps:**
1. Click "Edit" button on "Buy groceries" task
2. Modify:
   - Title: `Buy groceries and supplies`
   - Description: `Milk, eggs, bread, coffee, and paper towels`
3. Click "Update Task" button

**Expected Results:**
- ✅ Form closes
- ✅ Task updates with new title and description
- ✅ "Updated" timestamp changes
- ✅ Task remains in same position

**Cancel Test:**
- Click "Edit", make changes, then click "Cancel"
- ✅ Form closes without saving changes

---

### Test 2.6: Delete Task

**Steps:**
1. Click "Delete" button on "Exercise" task
2. Confirm deletion in browser alert

**Expected Results:**
- ✅ Confirmation dialog appears: "Are you sure you want to delete this task?"
- ✅ After confirming, task disappears immediately
- ✅ Section header updates: "Active Tasks (3)"

**Cancel Test:**
- Click "Delete", then click "Cancel" in confirmation
- ✅ Task remains in list

---

### Test 2.7: Empty State

**Steps:**
1. Delete all remaining tasks one by one
2. Observe the UI when no tasks exist

**Expected Results:**
- ✅ Empty state component appears
- ✅ Shows message: "No tasks yet"
- ✅ Shows "Create Your First Task" button
- ✅ Clicking button opens create form

---

## Test Suite 3: User Isolation & Security

### Test 3.1: Create Second User

**Steps:**
1. Sign out from `testuser1@example.com`
2. Navigate to `/signup`
3. Create new account:
   - Email: `testuser2@example.com`
   - Password: `SecurePass456!@#`
4. After auto-signin, create 2 tasks:
   - "User 2 Task 1" / "This belongs to user 2"
   - "User 2 Task 2" / "Also belongs to user 2"

**Expected Results:**
- ✅ Signup succeeds
- ✅ Dashboard shows empty state initially (no tasks from user 1)
- ✅ Can create tasks successfully

---

### Test 3.2: Verify User Isolation

**Steps:**
1. Sign out from `testuser2@example.com`
2. Sign in as `testuser1@example.com`
3. Observe dashboard

**Expected Results:**
- ✅ Only sees their own tasks (not user 2's tasks)
- ✅ Cannot access or modify user 2's tasks
- ✅ Task count reflects only their tasks

**Backend Verification:**
- Check backend logs for user_id filtering
- Verify all API requests include proper JWT token
- Confirm backend enforces user_id matching

---

### Test 3.3: JWT Token Validation

**Steps:**
1. Sign in successfully
2. Open browser DevTools → Application → Cookies
3. Find `auth_token` cookie
4. Modify the token value to something invalid (e.g., change last character)
5. Refresh the page

**Expected Results:**
- ✅ Middleware detects invalid token
- ✅ Redirects to `/signin`
- ✅ Invalid cookie is cleared
- ✅ Error logged in browser console: "Token validation failed"

---

### Test 3.4: Expired Token Handling

**Steps:**
1. Sign in successfully
2. Wait for token to expire (or manually set expired token)
3. Try to perform any action (create task, etc.)

**Expected Results:**
- ✅ API returns 401 Unauthorized
- ✅ Frontend clears token and redirects to `/signin?error=session_expired`
- ✅ Error message: "Your session has expired. Please sign in again."

---

## Test Suite 4: Error Handling

### Test 4.1: Network Errors

**Steps:**
1. Stop the backend server
2. Try to sign in or create a task

**Expected Results:**
- ✅ Error message displayed: "An unexpected error occurred. Please try again."
- ✅ Form remains usable (can retry after backend restarts)

---

### Test 4.2: Validation Errors

**Steps:**
1. Try to create task with empty title
2. Try to create task with 201-character title
3. Try to signup with weak password

**Expected Results:**
- ✅ Field-specific error messages displayed
- ✅ Error messages clear when user starts typing
- ✅ Form doesn't submit until validation passes

---

### Test 4.3: Backend Validation Errors

**Steps:**
1. Try to signup with email that already exists
2. Try to signin with wrong password

**Expected Results:**
- ✅ Generic error message: "Invalid email or password" (prevents user enumeration)
- ✅ No indication whether email exists or password is wrong

---

## Test Suite 5: UI/UX Verification

### Test 5.1: Loading States

**Steps:**
1. Observe loading indicators during:
   - Initial page load
   - Signin/signup
   - Task list loading
   - Task creation/update/deletion

**Expected Results:**
- ✅ Loading spinner shown during auth operations
- ✅ "Loading tasks..." message while fetching
- ✅ Button text changes: "Sign In" → "Signing in...", "Create Task" → "Creating..."
- ✅ Buttons disabled during submission

---

### Test 5.2: Responsive Design (Basic Check)

**Steps:**
1. Resize browser window to mobile size (375px width)
2. Test all functionality on mobile viewport

**Expected Results:**
- ✅ Layout adapts to mobile screen
- ✅ All buttons and forms remain usable
- ✅ Text remains readable
- ✅ No horizontal scrolling

---

### Test 5.3: Keyboard Navigation

**Steps:**
1. Navigate forms using Tab key
2. Submit forms using Enter key
3. Close dialogs using Escape key (if applicable)

**Expected Results:**
- ✅ Tab order is logical
- ✅ Enter submits forms
- ✅ Focus indicators visible

---

## Test Suite 6: Browser Compatibility

### Test 6.1: Cross-Browser Testing

**Browsers to Test:**
- Chrome/Edge (Chromium)
- Firefox
- Safari (if available)

**Expected Results:**
- ✅ All functionality works in all browsers
- ✅ Styling consistent across browsers
- ✅ No console errors

---

## Known Issues & Limitations

### Security Warnings (See SECURITY-NOTES.md)

⚠️ **CRITICAL ISSUES (Require Backend Fixes):**
1. Tokens stored in localStorage (XSS vulnerable)
2. Cookies set via JavaScript (missing httpOnly flag)
3. No CSRF protection
4. No rate limiting on auth endpoints

⚠️ **Current Mitigations:**
- Token validation in middleware (signature + expiration)
- Generic error messages (prevents user enumeration)
- Strong password requirements
- Open redirect protection

---

## Test Results Template

Copy this template and fill in results:

```
## Test Execution Results

**Date:** ___________
**Tester:** ___________
**Environment:** Frontend: localhost:3001, Backend: localhost:8000

### Suite 1: Authentication
- [ ] Test 1.1: User Signup - PASS / FAIL / BLOCKED
- [ ] Test 1.2: User Signin - PASS / FAIL / BLOCKED
- [ ] Test 1.3: Protected Routes - PASS / FAIL / BLOCKED
- [ ] Test 1.4: Session Persistence - PASS / FAIL / BLOCKED

### Suite 2: Task Management
- [ ] Test 2.1: Create Task - PASS / FAIL / BLOCKED
- [ ] Test 2.2: Multiple Tasks - PASS / FAIL / BLOCKED
- [ ] Test 2.3: Mark Complete - PASS / FAIL / BLOCKED
- [ ] Test 2.4: Unmark Complete - PASS / FAIL / BLOCKED
- [ ] Test 2.5: Edit Task - PASS / FAIL / BLOCKED
- [ ] Test 2.6: Delete Task - PASS / FAIL / BLOCKED
- [ ] Test 2.7: Empty State - PASS / FAIL / BLOCKED

### Suite 3: User Isolation
- [ ] Test 3.1: Second User - PASS / FAIL / BLOCKED
- [ ] Test 3.2: User Isolation - PASS / FAIL / BLOCKED
- [ ] Test 3.3: Token Validation - PASS / FAIL / BLOCKED
- [ ] Test 3.4: Expired Token - PASS / FAIL / BLOCKED

### Suite 4: Error Handling
- [ ] Test 4.1: Network Errors - PASS / FAIL / BLOCKED
- [ ] Test 4.2: Validation Errors - PASS / FAIL / BLOCKED
- [ ] Test 4.3: Backend Errors - PASS / FAIL / BLOCKED

### Suite 5: UI/UX
- [ ] Test 5.1: Loading States - PASS / FAIL / BLOCKED
- [ ] Test 5.2: Responsive Design - PASS / FAIL / BLOCKED
- [ ] Test 5.3: Keyboard Navigation - PASS / FAIL / BLOCKED

### Suite 6: Browser Compatibility
- [ ] Chrome/Edge - PASS / FAIL / BLOCKED
- [ ] Firefox - PASS / FAIL / BLOCKED
- [ ] Safari - PASS / FAIL / BLOCKED

**Issues Found:**
1.
2.
3.

**Notes:**

```

---

## Quick Start Testing

**Fastest way to verify MVP works:**

1. Open http://localhost:3001
2. Click "Get Started"
3. Signup: `test@example.com` / `TestPass123!@#`
4. Create task: "Test Task" / "Testing the app"
5. Mark complete, edit, delete
6. Sign out and sign back in
7. Verify task persistence

**If all above works:** ✅ MVP is functional!

---

## Next Steps After Testing

1. **If tests pass:** Proceed with UI refinement or Phase 5-7 features
2. **If tests fail:** Document issues and fix critical bugs
3. **Security:** Coordinate with backend team on SECURITY-NOTES.md issues
4. **Deployment:** Prepare for production environment
