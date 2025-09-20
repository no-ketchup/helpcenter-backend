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
├── Dockerfile              # Backend container build
├── Makefile                # Dev/CI commands
├── README.md
├── app/                    # Application source
│   ├── core/               # Core setup (db, main, settings)
│   ├── data/               # Seeds / data bootstrap
│   ├── domain/             # Models, resolvers, schema
│   ├── mappers/            # Placeholder for data mappers
│   ├── migrations/         # Alembic migrations
│   └── utils/              # Helpers
├── docker-compose.yaml     # Local stack (Postgres + backend)
├── requirements.txt        # Python dependencies
└── tests/                  # Pytest suite
```

---

## Setup

### ### Makefile Targets
- `build` / `up` / `down` — manage containers
- `migrate` — run Alembic migrations
- `test` / `ci-test` — run test suite (local or CI mode)
- `logs` — tail container logs
- `shell` — open backend shell
- `prod-*` — production deploy helpers