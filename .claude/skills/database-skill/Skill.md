---
name: database-skill
description: Design and manage databases including schema design, table creation, and migrations for scalable applications.
---

# Database Design & Management

## Instructions

1. **Schema Design**
   - Identify core entities and relationships
   - Normalize data to reduce redundancy
   - Define primary keys and foreign keys
   - Plan for scalability and future changes

2. **Table Creation**
   - Define clear column names and data types
   - Apply constraints (NOT NULL, UNIQUE, DEFAULT)
   - Use indexes for frequently queried fields
   - Maintain consistent naming conventions

3. **Migrations**
   - Create versioned migration files
   - Support up and down migrations
   - Ensure migrations are idempotent
   - Apply migrations safely across environments

4. **Relationships**
   - One-to-one, one-to-many, many-to-many
   - Enforce referential integrity
   - Use cascading rules thoughtfully

5. **Data Integrity & Performance**
   - Validate data at the database level
   - Use transactions for multi-step operations
   - Optimize queries with indexes

## Best Practices
- Design schema before writing application code
- Keep migrations small and reversible
- Avoid breaking changes in production
- Use snake_case or camelCase consistently
- Document schema decisions
- Follow ACID principles

## Example Structure

### Users Table
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- up
ALTER TABLE users ADD COLUMN username VARCHAR(100);

-- down
ALTER TABLE users DROP COLUMN username;
