# Help Center Backend

A mostly production-ready help center backend built with FastAPI, GraphQL, and PostgreSQL. Features a complete CI/CD pipeline with Docker, GitHub Actions, and Cloud Run deployment.

## Background & Motivation

This backend started as an experiment to fill the gaps left by no-code (would not recommend) and SaaS headless CMS products.  
I tested multiple approaches, from commercial SaaS solutions to a self-hosted Payload CMS instance — but each came with trade-offs that didn’t fit the needs of a robust help center:

- Limited flexibility for custom editor features
- Harder integration with GraphQL and domain-driven design
- Limited or locked-down CI/CD workflows

I ended up building the backend myself.  
The real intention of this project is to explore and implement **a solid CI/CD pipeline in a more realistic environment**:

- Dockerized development and production workflows  
- GitHub Actions for testing, linting, and security scans  
- Automated builds and deployments to Cloud Run  
- Environment-specific configurations with secrets management  

By treating this as a production-grade project, I get to explore what it takes to ship reliable backend services in modern environments and do my homework for future projects.

## Architecture

- **Backend**: FastAPI + GraphQL (Strawberry)
- **Database**: Neon DB (PostgreSQL) with connection pooling
- **Cache**: Redis for rate limiting and session management
- **Media Storage**: Google Cloud Storage
- **Deployment**: Google Cloud Run with automated CI/CD
- **CI/CD**: GitHub Actions with environment-specific deployments
- **Frontend**: Vercel (Next.js)

## Features

- **GraphQL API**: Type-safe queries and mutations with Strawberry
- **REST API**: Developer editor endpoints for content management
- **Rich Text Support**: JSON-based content blocks for guides
- **Media Management**: File upload with GCS integration
- **Rate Limiting**: Redis-based rate limiting with different limits per endpoint
- **Structured Logging**: JSON logs with correlation IDs and request tracking
- **Input Validation**: Comprehensive Pydantic validation with custom validators
- **Test Coverage**: Full test suite with async support and database isolation
- **Docker Support**: Multi-stage builds for development and production
- **CLI Editor**: Terminal-based content management tool

## Quick Start

### Prerequisites

- Python 3.11+
- Docker
- Neon DB account
- Google Cloud account

### 1. Setup

```bash
git clone <repo>
cd helpcenter-backend
cp env.example .env.local
# Edit .env.local with your actual values
```

### 2. Configure Environment

The `env.example` file contains all required environment variables with placeholder values. Copy it to `.env.local` and update with your actual values:

- **Database**: Set your Neon DB connection details
- **Redis**: For rate limiting (use `redis://redis:6379` for local development)
- **Google Cloud**: Set your GCS bucket and service account
- **Security**: Generate strong secret keys
- **CORS**: Add your frontend domains

### 3. Run with Docker

```bash
# Start development environment
make dev

# Run tests
make test

# Run quick tests (no cleanup)
make test-quick
```

## Development

### Available Commands

```bash
make help          # Show all commands
make dev           # Start development environment
make dev-stop      # Stop development environment (NOT ALLOWED IN PRODUCTION)
make test          # Run full test suite with cleanup (TEST-ONLY TARGET)
make test-quick    # Run tests without cleanup (TEST-ONLY TARGET)
make migrate       # Run database migrations
make build         # Build Docker images (NOT ALLOWED IN PRODUCTION)
make build-prod    # Build production Docker image
make logs          # View logs (NOT ALLOWED IN PRODUCTION)
make shell         # Open container shell (NOT ALLOWED IN PRODUCTION)
make editor        # Run the help center editor (NOT ALLOWED IN PRODUCTION)
make health        # Check API health
make lint          # Run code linting (NOT ALLOWED IN PRODUCTION)
make format        # Format code with black (NOT ALLOWED IN PRODUCTION)
```

### Production Safety

The Makefile includes production safety checks that prevent certain commands from running in production environments:

- **Test-only targets**: `test`, `test-quick`, `ci-test` - These always use test databases and are blocked in production
- **Development-only targets**: `build`, `clean`, `prune`, `logs`, `shell`, `editor`, `db-shell`, `db-list`, `dev-stop`, `lint`, `format` - These are blocked in production for security
- **Production targets**: `prod-up`, `prod-down`, `prod-clean`, `prod-migrate` - These are specifically designed for production use

### Environment-Specific Usage

```bash
# Development (uses .env.local)
make dev
make test
make build

# Production (requires environment variables to be set)
ENVIRONMENT=production make prod-up
ENVIRONMENT=production make prod-migrate
```

### Project Structure

```
app/
├── core/           # Core functionality
│   ├── db.py      # Database configuration with connection pooling
│   ├── logging.py # Structured JSON logging
│   ├── middleware.py # Request/response middleware
│   ├── rate_limiting.py # Redis-based rate limiting
│   └── settings.py # Application settings
├── domain/         # Domain logic
│   ├── models/    # SQLModel entities
│   ├── dtos/      # Data transfer objects
│   ├── resolvers/ # GraphQL resolvers
│   ├── schema/    # GraphQL schemas
│   └── rest/      # REST API endpoints
├── repositories/   # Data access layer
├── services/       # Business logic
└── main.py        # FastAPI application

scripts/
├── demo/          # Demo scripts and CLI editor
├── migrate.py     # Database migration script
└── deploy-cloud-run.sh # Cloud Run deployment

tests/             # Comprehensive test suite
├── categories/    # Category tests (REST + GraphQL)
├── guides/        # Guide tests (REST + GraphQL)
├── media/         # Media tests (REST + GraphQL)
└── graphql/       # GraphQL integration tests
```

## CLI Editor

Terminal-based content management tool for creating and managing help center content:

```bash
make editor
```

### Editor Features

- Global exit commands (`q`, `quit`, `exit`)
- Keyboard interrupt support (`Ctrl+C`)
- Help system (`h` command)
- Rich text support with JSON content blocks
- Media file upload and management
- GraphQL query testing
- Organized content viewing

### Editor Commands

- Create and manage categories
- Create and manage guides with rich text
- Upload and attach media files
- Test GraphQL queries
- View all content in organized tables

## API Endpoints

### GraphQL

- `POST /graphql` - GraphQL endpoint with rate limiting
- Queries: `getCategories`, `getCategory`, `getGuides`, `getGuide`
- Mutations: `submitFeedback`

### REST API

- `GET /health` - Health check with rate limiting
- `POST /dev-editor/categories` - Create category (dev editor)
- `GET /dev-editor/categories` - List categories (dev editor)
- `POST /dev-editor/guides` - Create guide (dev editor)
- `POST /dev-editor/media/upload` - Upload media (dev editor)

## Testing

```bash
# Run full test suite with cleanup
make test

# Run quick tests (no cleanup)
make test-quick

# Run specific test file
docker compose run --rm -e ENVIRONMENT=test backend pytest tests/categories/

# Run with coverage
docker compose run --rm -e ENVIRONMENT=test backend pytest --cov=app tests/
```

### Test Coverage

- **Categories**: REST and GraphQL endpoints
- **Guides**: REST and GraphQL endpoints with rich text
- **Media**: File upload and management
- **GraphQL**: Integration tests
- **Health**: Health check endpoint
- **Rate Limiting**: Rate limit enforcement
- **Database**: Test isolation with cleanup

## Deployment

### Automated CI/CD

The project includes a complete CI/CD pipeline with GitHub Actions:

1. **Test**: Runs full test suite with Docker using isolated test database
2. **Security Scan**: Trivy vulnerability scanning with SARIF upload
3. **Build**: Creates production Docker image using Dockerfile.prod
4. **Deploy**: Automatically deploys to Cloud Run with environment-specific secrets

#### CI/CD Environment Variables

The CI/CD pipeline uses hardcoded test values for testing and injects real secrets only during deployment:

- **Test Phase**: Uses `postgres:postgres@db:5432/test_db` for isolated testing
- **Deployment Phase**: Injects production secrets from GitHub Secrets
- **Environment Validation**: Makefile validates required environment variables are present

### Manual Deployment

1. **Setup GCS Bucket**:
   ```bash
   gsutil mb gs://your-helpcenter-bucket
   gsutil iam ch allUsers:objectViewer gs://your-helpcenter-bucket
   ```

2. **Deploy with Script**:
   ```bash
   ./scripts/deploy-cloud-run.sh production
   ```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL_ASYNC` | Neon DB async connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `GCS_BUCKET_NAME` | Google Cloud Storage bucket | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | GCS service account key | Yes |
| `SECRET_KEY` | Application secret key | Yes |
| `DEV_EDITOR_KEY` | Editor authentication key | Yes |
| `ALLOWED_ORIGINS` | CORS allowed origins | Yes |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |
| `ENVIRONMENT` | Environment (development, staging, production) | No |

## Free Tier Limits

- **Neon DB**: 0.5GB storage, 10GB transfer/month
- **Redis**: 30MB memory, 30 connections (Redis Cloud free tier)
- **Google Cloud Storage**: 5GB storage, 1GB transfer/month
- **Google Cloud Run**: 2M requests/month, 400K GB-seconds compute
- **Vercel**: 100GB bandwidth/month

In layman's terms, this stack should cover a deep exploration.

## Architecture Decisions

- **Domain-Driven Design**: Clear separation of concerns with domain logic
- **Connection Pooling**: AsyncAdaptedQueuePool for production, NullPool for tests
- **Rate Limiting**: Redis-based with different limits per endpoint type
- **Structured Logging**: JSON logs with correlation IDs for observability
- **Test Isolation**: Database cleanup between tests for reliability
- **Docker-First**: All operations run in containers for consistency
- **Production Safety**: Makefile blocks dangerous commands in production environments
- **Environment Validation**: Explicit validation of required environment variables
- **CI/CD Isolation**: Test phase uses hardcoded values, deployment phase uses secrets

## License

MIT License