---
name: backend-skill
description: Build backend services by generating API routes, handling requests and responses, and connecting to databases.
---

# Backend Development

## Instructions

1. **Route Generation**
   - Define RESTful or RPC-based endpoints
   - Organize routes by feature or resource
   - Support CRUD operations
   - Apply versioning where needed

2. **Request Handling**
   - Parse request parameters and body
   - Validate input data
   - Handle authentication and authorization
   - Manage middleware and hooks

3. **Response Handling**
   - Return consistent response formats
   - Use proper HTTP status codes
   - Handle errors gracefully
   - Support pagination and filtering

4. **Database Connection**
   - Establish secure DB connections
   - Use ORM or query builders
   - Manage connection pooling
   - Handle transactions safely

5. **Business Logic Layer**
   - Separate logic from route definitions
   - Reuse services across endpoints
   - Keep controllers thin and focused

## Best Practices
- Follow REST or API design standards
- Validate all external inputs
- Use environment variables for secrets
- Keep routes stateless
- Log errors and key events
- Write modular, testable code

## Example Structure

### API Route
```ts
POST /api/users
- validate request body
- call service layer
- persist data to database
- return JSON response

connectDB()
- initialize connection
- run migrations if needed
- expose client to services
