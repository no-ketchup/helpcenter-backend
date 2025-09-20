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

## Project Structure
```
.
├── alembic/            # Alembic migrations
├── app/                # Application code
│   ├── main.py         # FastAPI entrypoint
│   ├── db.py           # DB session & engine
│   ├── schema.py       # GraphQL schema
│   └── resolvers.py    # Queries & mutations
├── docker-compose.yaml # Unified compose file
├── Dockerfile
├── Makefile
├── requirements.txt
├── .env                # Development settings
├── .env.test           # Test settings
└── .env.prod           # Production settings
```

---

## Setup

### Prerequisites
- Docker + Docker Compose
- Make (optional but recommended)

### Environment
Copy `.env` files and adjust if needed:
```bash
cp .env .env.local      # For custom dev overrides
```

---

## Development

Start backend + DB:
```bash
make up
```

Stop & clean up:
```bash
make down
```

Run DB migrations:
```bash
make migrate
```

---

## Testing

Run interactive tests (containers kept alive for debugging):
```bash
make test
```

Run CI-style tests (containers exit after run):
```bash
make ci-test
```

---

## Production

Build with production config:
```bash
make build ENV_FILE=.env.prod
```

Deploy (with `.env.prod`):
```bash
ENV_FILE=.env.prod make up
```

---

## Secrets
- In production, never commit secrets to `.env.prod`.  
- Use CI/CD secrets or a secret manager to inject sensitive values (e.g., `SECRET_KEY`, DB credentials).

---

## Roadmap
- Admin interface for content management (create/edit/delete)
- Rich text support in GraphQL schema
- Blob storage integration (media uploads)
- Deployment scripts for AWS/GCP
