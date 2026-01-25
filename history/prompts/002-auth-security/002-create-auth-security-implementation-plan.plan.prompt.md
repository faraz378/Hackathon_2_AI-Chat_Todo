---
id: 002
title: create-auth-security-implementation-plan
stage: plan
date: 2026-01-13
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-auth-security
branch: 002-auth-security
user: user
command: /sp.plan
labels: ["authentication", "security", "jwt", "architecture", "planning"]
links:
  spec: specs/002-auth-security/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-auth-security/plan.md
  - specs/002-auth-security/research.md
  - specs/002-auth-security/data-model.md
  - specs/002-auth-security/contracts/auth-api.yaml
  - specs/002-auth-security/quickstart.md
tests:
  - null
---

## Prompt

/sp.plan

Create:
- Auth flow architecture (Next.js Better Auth → JWT → FastAPI)
- JWT verification middleware for FastAPI
- Frontend API client strategy for token attachment

Decisions needing documentation:
- JWT payload fields required by backend
- Token expiration duration and validation rules
- Strategy for matching JWT user identity with route user_id

Testing & validation:
- Verify unauthorized requests return 401
- Confirm JWT signature validation using shared secret
- Ensure authenticated users only access their own tasks

## Response snapshot

Created comprehensive implementation plan for Authentication & Security (Spec-2) with complete architecture, research, data models, API contracts, and quickstart guide.

**Files Created** (5 documents, 1,200+ lines):

1. **plan.md** (450 lines)
   - Summary and technical context
   - Constitution checks (all passed)
   - Project structure (backend + frontend)
   - Authentication flow diagrams
   - JWT verification middleware flow
   - Testing & validation strategy
   - Key decisions documented

2. **research.md** (350 lines)
   - 6 research areas with decisions and rationale
   - JWT library: PyJWT 2.8.0 (vs python-jose)
   - Password hashing: bcrypt work factor 12 (vs argon2)
   - Better Auth integration strategy
   - JWT middleware: Dependency injection (vs middleware class)
   - Token storage: localStorage for Spec-2 (plan for httpOnly cookies)
   - User ID verification: Dependency injection pattern
   - Security considerations and threat model

3. **data-model.md** (400 lines)
   - User model extension (email, password_hash fields)
   - Database migration strategy
   - Complete SQL schema with indexes and triggers
   - JWT token structure (header, payload, signature)
   - Token generation and verification implementation
   - Pydantic schemas (SignupRequest, SigninRequest, TokenResponse)
   - Data validation rules
   - Performance characteristics

4. **contracts/auth-api.yaml** (550 lines)
   - Complete OpenAPI 3.0 specification
   - 2 auth endpoints: POST /auth/signup, POST /auth/signin
   - 5 protected task endpoints with JWT requirement
   - Request/response schemas with examples
   - Error responses with codes (EMAIL_EXISTS, INVALID_CREDENTIALS, MISSING_TOKEN, etc.)
   - Security scheme: Bearer token (JWT)

5. **quickstart.md** (450 lines)
   - Backend setup (dependencies, environment, migration)
   - Frontend setup (Next.js, Better Auth)
   - 6 test scenarios with curl commands
   - Validation checklist (15 items)
   - Troubleshooting guide (5 common issues)
   - Performance testing instructions

**Key Architectural Decisions**:

1. **JWT Payload Structure**:
   - Standard claims: sub (user_id), email, iat, exp
   - 24-hour expiration, no refresh tokens in Spec-2
   - Minimal payload for performance

2. **User ID Verification**:
   - Middleware extracts JWT user_id
   - Compares with route parameter user_id
   - Returns 403 FORBIDDEN on mismatch (not 404 to avoid info leak)

3. **Password Hashing**:
   - bcrypt with work factor 12 (~250ms per hash)
   - Built-in salt generation
   - Industry standard security

4. **Token Storage**:
   - localStorage for Spec-2 (Better Auth compatible)
   - Future migration path to httpOnly cookies documented
   - XSS mitigation via Next.js built-in protection

5. **Authentication Flow**:
   - Stateless JWT verification (no DB lookups)
   - Dependency injection pattern for middleware
   - Structured error responses with specific codes

**Architecture Highlights**:

- **Auth Flow Diagram**: Complete flow from signup → signin → JWT generation → token verification → protected resource access
- **JWT Middleware Flow**: Detailed flowchart showing token extraction, signature verification, user ID matching, and error handling
- **Database Schema**: User model extension with email index, password_hash storage, and migration strategy
- **API Contracts**: OpenAPI spec with 7 endpoints, 8 error codes, and complete request/response examples

**Testing Strategy**:

- 7 test categories defined (signup, signin, JWT verification, protected endpoints, integration, security)
- 20+ specific test cases documented
- Security validation checklist (7 items)
- Performance benchmarks (JWT verification <50ms, password hashing ~250ms)

**Constitution Compliance**:

- ✅ Pre-design check: All 7 principles passed
- ✅ Post-design check: All 7 principles passed
- No complexity violations
- Ready for Phase 2 (Task Breakdown)

## Outcome

- ✅ Impact: Complete implementation plan ready for task breakdown. All architectural decisions documented with rationale.
- 🧪 Tests: Testing strategy defined with 20+ test cases across 7 categories
- 📁 Files: 5 files created (plan, research, data-model, contracts, quickstart)
- 🔁 Next prompts: /sp.tasks to generate task breakdown from this plan
- 🧠 Reflection: Plan successfully addresses all user requirements (auth flow architecture, JWT middleware, frontend token strategy, user ID matching). All decisions documented with clear rationale. Constitution checks passed both pre and post design.

## Evaluation notes (flywheel)

- Failure modes observed: None - all planning artifacts created successfully
- Graders run and results (PASS/FAIL): Constitution checks PASS (14/14 items across pre and post design)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
