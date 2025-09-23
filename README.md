# Help Center Backend

A production-ready help center backend built with FastAPI, GraphQL, and PostgreSQL. Designed for learning modern CI/CD practices with a real-world application.

## Architecture

- **Backend**: FastAPI + GraphQL (Strawberry)
- **Database**: Neon DB (PostgreSQL)
- **Media Storage**: Google Cloud Storage
- **Deployment**: Google Cloud Run
- **CI/CD**: GitHub Actions
- **Frontend**: Vercel

## Features

- **GraphQL API**: Type-safe queries and mutations
- **REST API**: Developer editor endpoints
- **Rich Text Support**: JSON-based content blocks
- **Media Management**: File upload with GCS integration
- **Structured Logging**: JSON logs with correlation IDs
- **Input Validation**: Comprehensive data validation
- **Test Coverage**: Full test suite with async support
- **Docker Support**: Containerized development and production

## Quick Start

### Prerequisites

- Python 3.11+
- Docker
- Neon DB account
- Google Cloud account

### 1. Setup

```bash
git clone <your-repo>
cd helpcenter-backend
cp env.example .env.local
```

### 2. Configure Environment

Update `.env.local` with your credentials:

```bash
# Database
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/helpcenter?sslmode=require

# Google Cloud Storage
GCS_BUCKET_NAME=your-helpcenter-bucket
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key
DEV_EDITOR_KEY=dev-editor-key
```

### 3. Run with Docker

```bash
# Start database
make up

# Run migrations
make migrate

# Run tests
make test
```

## Development

### Available Commands

```bash
make help          # Show all commands
make up            # Start services
make down          # Stop services
make test          # Run tests
make migrate       # Run migrations
make logs          # View logs
make shell         # Open container shell
make editor        # Run the help center editor
```

### Project Structure

```
app/
├── core/           # Core functionality
│   ├── db.py      # Database configuration
│   ├── logging.py # Structured logging
│   ├── middleware.py # Request middleware
│   └── validation.py # Input validation
├── domain/         # Domain logic
│   ├── models/    # SQLModel entities
│   ├── dtos/      # Data transfer objects
│   ├── resolvers/ # GraphQL resolvers
│   └── schema/    # GraphQL schemas
├── repositories/   # Data access layer
├── services/       # Business logic
└── main.py        # FastAPI application

scripts/
├── demo/          # Demo scripts
├── test/          # Test utilities
└── deploy.sh      # Deployment script

docs/              # Documentation
tests/             # Test suite
```

## Help Center Editor

The project includes a terminal-based editor for managing content:

```bash
make editor
```

### Editor Features

- **Global Exit Commands**: Type `q`, `quit`, or `exit` at any prompt
- **Keyboard Interrupt**: Press `Ctrl+C` to exit
- **Help System**: Type `h` for help information
- **Rich Text Support**: JSON-based content blocks
- **Media Management**: Upload and attach files to guides
- **GraphQL Testing**: Test queries directly from the editor

### Editor Commands

- Create and manage categories
- Create and manage guides with rich text
- Upload and attach media files
- Test GraphQL queries
- View all content in organized tables

## API Endpoints

### GraphQL

- `POST /graphql` - GraphQL endpoint

### REST API

- `GET /health` - Health check
- `POST /dev-editor/categories` - Create category
- `POST /dev-editor/guides` - Create guide
- `POST /dev-editor/media/upload` - Upload media

## Testing

```bash
# Run all tests
make test

# Run specific test file
docker compose run --rm -e ENVIRONMENT=test backend pytest tests/categories/

# Run with coverage
docker compose run --rm -e ENVIRONMENT=test backend pytest --cov=app tests/
```

## Deployment

### Google Cloud Run

1. **Setup GCS Bucket**:
   ```bash
   gsutil mb gs://your-helpcenter-bucket
   gsutil iam ch allUsers:objectViewer gs://your-helpcenter-bucket
   ```

2. **Deploy**:
   ```bash
   gcloud run deploy helpcenter-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Neon DB connection string | Yes |
| `GCS_BUCKET_NAME` | Google Cloud Storage bucket | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | GCS service account key | Yes |
| `SECRET_KEY` | Application secret key | Yes |
| `DEV_EDITOR_KEY` | Editor authentication key | Yes |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |
| `ENVIRONMENT` | Environment (development, staging, production) | No |

## Free Tier Limits

- **Neon DB**: 0.5GB storage, 10GB transfer/month
- **Google Cloud Storage**: 5GB storage, 1GB transfer/month
- **Google Cloud Run**: 2M requests/month, 400K GB-seconds compute
- **Vercel**: 100GB bandwidth/month

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.