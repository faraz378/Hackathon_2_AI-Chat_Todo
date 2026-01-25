# Backend Core & Data Layer

Task management backend with RESTful API, JWT authentication, and user-scoped data handling.

## Quick Start

### Prerequisites
- Python 3.11 or higher
- Neon PostgreSQL account (free tier available at https://neon.tech)

### Setup

1. **Create Virtual Environment**
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**

Create `.env` file in `backend/` directory:
```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

# JWT Authentication Configuration
JWT_SECRET=your-super-secret-key-must-be-at-least-32-characters-long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

**Important**:
- Get your Neon connection string from https://neon.tech
- Replace `postgresql://` with `postgresql+asyncpg://`
- Add `?sslmode=require` at the end
- Generate a secure JWT_SECRET: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

4. **Run Database Migration** (if needed)
```bash
# Apply authentication fields migration
alembic upgrade head
```

5. **Run Development Server**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Verify Installation**
```bash
curl http://localhost:8000/docs
```

## Authentication

### Register a New User
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### Sign In
```bash
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### Access Protected Endpoints
```bash
# Save the token from signin response
TOKEN="your-jwt-token-here"

# Use token in Authorization header
curl -X GET http://localhost:8000/users/1/tasks \
  -H "Authorization: Bearer $TOKEN"
```

## API Documentation

- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html
```

## Project Structure

```
backend/
├── src/
│   ├── models/          # SQLModel database models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── api/
│   │   ├── routes/      # API endpoints (auth, tasks)
│   │   └── deps.py      # Authentication dependencies
│   ├── core/
│   │   ├── config.py    # Configuration
│   │   ├── database.py  # Database connection
│   │   └── security.py  # JWT and password utilities
│   └── main.py          # FastAPI app initialization
├── migrations/          # Database migrations
├── tests/               # Test suite
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Technology Stack

- **Framework**: FastAPI 0.104+
- **ORM**: SQLModel 0.0.14+
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT (PyJWT 2.8.0)
- **Password Hashing**: bcrypt (passlib 1.7.4)
- **Validation**: Pydantic 2.5+
- **Testing**: pytest 7.4+

## Security Features

✅ **Implemented**:
- JWT-based stateless authentication
- Password hashing with bcrypt (work factor 12)
- User data isolation (users can only access their own tasks)
- Token expiration (24 hours)
- Protected API endpoints with Bearer token authentication

⚠️ **Production Considerations**:
- Use HTTPS in production
- Store JWT_SECRET securely (environment variables, secrets manager)
- Consider implementing refresh tokens for longer sessions
- Add rate limiting to prevent brute force attacks
- Enable CORS only for trusted origins

## Support

For detailed setup instructions and troubleshooting, see:
- `specs/002-auth-security/quickstart.md` - Authentication setup guide
- `specs/002-auth-security/data-model.md` - Database schema
- `specs/002-auth-security/contracts/auth-api.yaml` - API contracts

