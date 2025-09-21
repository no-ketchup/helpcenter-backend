# Help Center Backend

A FastAPI + Strawberry GraphQL backend with SQLModel, Alembic migrations, and PostgreSQL.  
Supports development, testing, and production via Docker Compose with environment-specific `.env` files.

---

## Features
- FastAPI + Strawberry for GraphQL APIs
- SQLModel + Alembic for schema & migrations
- Async DB access with PostgreSQL
- Docker Compose for dev/test/prod
- CI/CD with GitHub Actions
- Makefile for common workflows

---

## Lesson learn

When developing using Docker Compose, .env.dev vs .env.test separation just keeps bleeding into each other because Compose decides what gets mounted at runtime.
Don't fight with the container orchestrator. Let it drive.