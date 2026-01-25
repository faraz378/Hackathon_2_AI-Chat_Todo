---
name: auth-skill
description: Implement secure authentication including sign up, sign in, password hashing, JWT-based auth, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **User Registration (Sign Up)**
   - Validate email and password inputs
   - Enforce strong password rules
   - Hash passwords before storing (bcrypt / argon2)
   - Prevent duplicate accounts

2. **User Login (Sign In)**
   - Verify credentials securely
   - Compare hashed passwords
   - Handle invalid login attempts gracefully
   - Return authentication tokens on success

3. **Password Security**
   - Use industry-standard hashing algorithms
   - Apply salting automatically
   - Never store plaintext passwords
   - Support password reset flows (optional)

4. **JWT Authentication**
   - Generate access tokens on login
   - Include user ID and role in payload
   - Set token expiration
   - Verify tokens on protected routes

5. **Better Auth Integration**
   - Configure Better Auth providers
   - Support email/password authentication
   - Enable session or token-based auth
   - Plug into existing backend framework (Next.js / FastAPI / Express)

## Best Practices
- Always hash passwords before database storage
- Use HTTPS-only cookies or Authorization headers
- Short-lived access tokens with refresh strategy
- Centralize auth logic in a dedicated module
- Return generic error messages for security
- Follow OWASP authentication guidelines

## Example Structure

### Sign Up (Backend)
```ts
POST /auth/signup
- validate input
- hash password
- save user
- return success response

POST /auth/signin
- verify user exists
- compare hashed password
- generate JWT
- return token

GET /profile
- verify JWT
- attach user to request
- return protected data
