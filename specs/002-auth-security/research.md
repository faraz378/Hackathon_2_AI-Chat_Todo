# Research: Authentication & Security

**Feature**: 002-auth-security | **Date**: 2026-01-13
**Phase**: 0 (Research) | **Plan**: [plan.md](plan.md)

## Research Summary

This document captures technology decisions and rationale for implementing JWT-based authentication with Better Auth frontend and FastAPI backend.

---

## 1. JWT Library Selection (Backend)

### Question
Which Python JWT library should we use: PyJWT or python-jose?

### Options Evaluated

| Library | Version | Pros | Cons |
|---------|---------|------|------|
| **PyJWT** | 2.8.0 | - Most popular (7.5k stars)<br>- Active maintenance<br>- Simple API<br>- Excellent FastAPI examples<br>- Built-in algorithm support | - Fewer features than jose<br>- No JWE support |
| **python-jose** | 3.3.0 | - More comprehensive (JWS, JWE, JWK)<br>- Used in FastAPI docs<br>- Cryptography backend | - More complex API<br>- Heavier dependency<br>- Slower updates |

### Decision: **PyJWT 2.8.0**

**Rationale**:
- Simpler API matches our needs (only need JWS, not JWE)
- Better performance for basic JWT operations
- More active development and security patches
- Sufficient for HS256 signing and verification
- Smaller dependency footprint

**Implementation**:
```python
import jwt
from datetime import datetime, timedelta

# Generate token
payload = {
    "sub": user_id,
    "email": user_email,
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(hours=24)
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Verify token
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    # Handle expired token
except jwt.InvalidTokenError:
    # Handle invalid token
```

---

## 2. Password Hashing Strategy

### Question
Which password hashing algorithm: bcrypt or argon2?

### Options Evaluated

| Algorithm | Library | Pros | Cons |
|-----------|---------|------|------|
| **bcrypt** | passlib[bcrypt] | - Industry standard<br>- Adaptive work factor<br>- Built-in salt<br>- Wide support<br>- Battle-tested | - Slower than argon2<br>- 72-byte password limit |
| **argon2** | passlib[argon2] | - Winner of PHC 2015<br>- Memory-hard (GPU resistant)<br>- Faster than bcrypt<br>- Configurable memory/time | - Newer (less battle-tested)<br>- More complex config<br>- Larger dependency |

### Decision: **bcrypt with work factor 12**

**Rationale**:
- Industry standard with 20+ years of security research
- Simpler configuration (single work factor parameter)
- Adequate security for our use case (not high-security banking)
- Better library support in passlib
- Work factor 12 provides ~250ms hash time (good balance)

**Implementation**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
password_hash = pwd_context.hash(plain_password)

# Verify password
is_valid = pwd_context.verify(plain_password, password_hash)
```

**Work Factor Justification**:
- Factor 10: ~100ms (too fast, vulnerable to brute force)
- Factor 12: ~250ms (recommended for 2024)
- Factor 14: ~1000ms (too slow for user experience)

---

## 3. Better Auth Integration (Frontend)

### Question
How to configure Better Auth for custom FastAPI backend with JWT?

### Research Findings

**Better Auth Capabilities**:
- Supports custom backend providers
- Built-in token storage management
- Automatic token refresh (if configured)
- Session management hooks
- TypeScript support

**Integration Strategy**:

1. **Custom Provider Configuration**:
```typescript
// lib/auth.ts
import { BetterAuth } from "better-auth"

export const auth = BetterAuth({
  providers: {
    credentials: {
      authorize: async (credentials) => {
        const response = await fetch(`${API_URL}/auth/signin`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(credentials)
        })

        if (!response.ok) return null

        const data = await response.json()
        return {
          id: data.user_id,
          email: credentials.email,
          accessToken: data.access_token
        }
      }
    }
  },
  session: {
    strategy: "jwt",
    maxAge: 24 * 60 * 60 // 24 hours
  }
})
```

2. **Token Storage**: Better Auth handles localStorage automatically
3. **Token Injection**: Use Better Auth's session hook to get token

### Decision: **Use Better Auth with custom credentials provider**

**Rationale**:
- Better Auth provides session management out of the box
- Custom provider allows integration with FastAPI backend
- Automatic token storage and retrieval
- Built-in hooks for token expiration handling

---

## 4. JWT Middleware Architecture

### Question
Should we use FastAPI dependency injection or middleware class for JWT verification?

### Options Evaluated

| Approach | Pros | Cons |
|----------|------|------|
| **Dependency Injection** | - Explicit per-route control<br>- Easy to test<br>- Clear dependencies<br>- FastAPI idiomatic | - Must add to each route<br>- More verbose |
| **Middleware Class** | - Automatic for all routes<br>- Single point of control<br>- Less code duplication | - Harder to exclude routes<br>- Less explicit<br>- Harder to test |

### Decision: **Dependency Injection with `Depends(get_current_user)`**

**Rationale**:
- More explicit and testable
- Easy to exclude specific routes (health checks, auth endpoints)
- FastAPI best practice for authentication
- Clear dependency graph
- Better error handling per route

**Implementation**:
```python
# api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """Extract and verify JWT token, return user_id."""
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="INVALID_TOKEN")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="EXPIRED_TOKEN")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")

# Usage in routes
@router.get("/users/{user_id}/tasks")
async def get_tasks(
    user_id: int,
    current_user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")
    # ... rest of endpoint
```

---

## 5. Token Storage Strategy (Frontend)

### Question
Where to store JWT tokens: localStorage, httpOnly cookies, or sessionStorage?

### Options Evaluated

| Storage | Security | Persistence | Accessibility | Recommendation |
|---------|----------|-------------|---------------|----------------|
| **localStorage** | ⚠️ XSS vulnerable | ✅ Survives browser close | ✅ JS accessible | Good for Spec-2 |
| **httpOnly Cookie** | ✅ XSS protected | ✅ Survives browser close | ❌ Not JS accessible | Best (future) |
| **sessionStorage** | ⚠️ XSS vulnerable | ❌ Lost on browser close | ✅ JS accessible | Not suitable |

### Decision: **localStorage for Spec-2, plan for httpOnly cookies in future**

**Rationale**:
- localStorage works with Better Auth out of the box
- Accessible to JavaScript for API client token injection
- Next.js provides built-in XSS protection (sanitization)
- Acceptable risk for Spec-2 (not handling financial data)
- Future migration path to httpOnly cookies documented

**Security Mitigations**:
- Next.js automatic XSS protection
- Content Security Policy headers
- Token expiration (24 hours)
- No sensitive data in token payload

**Future Improvement** (Spec-3+):
- Move to httpOnly cookies
- Backend sets cookie on signin
- Automatic cookie inclusion in requests
- Enhanced XSS protection

---

## 6. User ID Verification Strategy

### Question
How to enforce JWT user_id matches route user_id parameter?

### Options Evaluated

| Approach | Implementation | Pros | Cons |
|----------|----------------|------|------|
| **Middleware** | Global check before route | - Single point of control<br>- Automatic for all routes | - Hard to customize per route<br>- Complex route parsing |
| **Dependency** | `verify_user_match(user_id, current_user)` | - Explicit per route<br>- Easy to test<br>- Clear intent | - Must add to each route<br>- Code duplication |
| **Route-level** | Check inside each endpoint | - Maximum flexibility<br>- Custom logic per route | - High duplication<br>- Easy to forget |

### Decision: **Dependency injection with verification function**

**Implementation**:
```python
# api/deps.py
async def verify_user_access(
    user_id: int,
    current_user_id: int = Depends(get_current_user)
) -> int:
    """Verify current user can access resources for user_id."""
    if current_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Cannot access another user's resources"
                }
            }
        )
    return current_user_id

# Usage in routes
@router.get("/users/{user_id}/tasks")
async def get_tasks(
    user_id: int,
    verified_user_id: int = Depends(verify_user_access),
    db: AsyncSession = Depends(get_db_session)
):
    # verified_user_id == user_id guaranteed
    # ... rest of endpoint
```

**Rationale**:
- Explicit and testable
- Reusable across all protected routes
- Clear error messages
- FastAPI dependency injection handles the verification
- Single source of truth for access control logic

---

## Technology Stack Summary

### Backend Dependencies

```txt
# Add to backend/requirements.txt
PyJWT==2.8.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6  # For form data parsing
```

### Frontend Dependencies

```json
// Add to frontend/package.json
{
  "dependencies": {
    "better-auth": "^1.0.0",
    "next": "^16.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}
```

### Environment Variables

**Backend** (`.env`):
```bash
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET=your-super-secret-key-at-least-32-characters-long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

**Frontend** (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
JWT_SECRET=your-super-secret-key-at-least-32-characters-long  # Same as backend
```

---

## Security Considerations

### Threat Model

| Threat | Mitigation | Status |
|--------|------------|--------|
| Password theft | bcrypt hashing (work factor 12) | ✅ Implemented |
| Token theft (XSS) | Next.js XSS protection, CSP headers | ⚠️ Partial (localStorage) |
| Token theft (network) | HTTPS only in production | ⚠️ Production requirement |
| Brute force signin | Rate limiting (future) | ❌ Out of scope (Spec-2) |
| Token replay | Expiration (24 hours) | ✅ Implemented |
| User impersonation | User ID verification | ✅ Implemented |
| SQL injection | SQLModel ORM parameterization | ✅ Implemented |

### Security Checklist

- ✅ Passwords hashed with bcrypt (never stored plaintext)
- ✅ JWT tokens signed with secret (HMAC-SHA256)
- ✅ Token expiration enforced (24 hours)
- ✅ User ID verification on every protected request
- ✅ Structured error responses (no info leakage)
- ✅ Environment variables for secrets (no hardcoding)
- ⚠️ HTTPS required in production (deployment concern)
- ⚠️ Rate limiting recommended (future enhancement)

---

## Performance Benchmarks

### Expected Latencies

| Operation | Target | Notes |
|-----------|--------|-------|
| Password hash (signup) | ~250ms | bcrypt work factor 12 |
| Password verify (signin) | ~250ms | bcrypt work factor 12 |
| JWT generation | <5ms | HMAC-SHA256 signing |
| JWT verification | <5ms | HMAC-SHA256 verification |
| Total auth overhead | <50ms | Per protected request |

### Optimization Strategies

1. **Async password hashing**: Use `asyncio.to_thread()` to avoid blocking
2. **JWT caching**: No caching needed (stateless verification is fast)
3. **Connection pooling**: Already configured in Spec-1 (pool_size=5)
4. **Database indexes**: Email index for user lookup during signin

---

## Open Questions & Future Work

### Deferred to Future Specs

1. **Refresh Tokens**: Not implemented in Spec-2 (24-hour expiration acceptable)
2. **Rate Limiting**: Should be added for production (prevent brute force)
3. **Email Verification**: Out of scope for Spec-2
4. **Password Reset**: Out of scope for Spec-2
5. **OAuth Providers**: Out of scope for Spec-2
6. **Multi-Factor Auth**: Out of scope for Spec-2

### Migration Path

**From Spec-1 to Spec-2**:
1. Add email and password_hash columns to User table
2. Existing users will need to be migrated (manual process or admin tool)
3. Backward compatibility: Keep user_id in URL for now (matches Spec-1 pattern)

**From Spec-2 to Spec-3** (hypothetical):
1. Add refresh tokens for longer sessions
2. Migrate from localStorage to httpOnly cookies
3. Add rate limiting middleware
4. Implement email verification flow

---

## Research Conclusion

All technology decisions have been made and documented. The chosen stack (PyJWT, bcrypt, Better Auth, dependency injection) provides a secure, performant, and maintainable authentication system that integrates cleanly with the existing Spec-1 backend.

**Ready for**: Phase 1 (Design) - Create detailed data models and API contracts.
