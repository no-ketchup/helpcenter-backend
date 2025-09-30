# Help Center - Separated Architecture

This is the Phase 1 MVP separation of the help center backend into microservices.

## Architecture

```
helpcenter-backend/
├── helpcenter-common/          # Shared components
│   ├── core/                   # Database, logging, settings, etc.
│   ├── domain/                 # Models, DTOs, resolvers, REST endpoints
│   ├── services/               # Business logic
│   ├── repositories/           # Data access
│   └── utils/                  # Utilities
├── helpcenter-graphql-api/     # Public GraphQL API (Cloud Run)
│   ├── main.py                 # FastAPI app with GraphQL only
│   ├── requirements.txt        # Dependencies
│   └── Dockerfile              # Container config
├── helpcenter-editor-api/      # Private REST API (Cloud Function)
│   ├── main.py                 # FastAPI app with REST endpoints
│   ├── requirements.txt        # Dependencies
│   ├── Dockerfile              # Container config
│   └── deploy-cloud-function.sh # Deployment script
└── .github/workflows/          # CI/CD pipelines
    └── separated-ci.yaml       # New separated CI/CD
```

## Services

### 1. GraphQL API (Public)
- **Purpose**: Public API for frontend consumption
- **Deployment**: Google Cloud Run
- **Endpoints**: `/graphql`, `/health`
- **Authentication**: None (public)

### 2. Editor API (Private)
- **Purpose**: Content management operations
- **Deployment**: Google Cloud Function
- **Endpoints**: `/dev-editor/*`
- **Authentication**: API key (`x-dev-editor-key` header)

### 3. Common Package
- **Purpose**: Shared code between services
- **Contains**: Models, DTOs, services, repositories, core utilities
- **Usage**: Imported by both APIs

## Development

### Local Development

```bash
# Install common package
cd helpcenter-common
pip install -r requirements.txt

# Run GraphQL API
cd helpcenter-graphql-api
pip install -r requirements.txt
uvicorn main:app --reload

# Run Editor API
cd helpcenter-editor-api
pip install -r requirements.txt
functions-framework --target=editor_api --reload
```

### Testing

```bash
# Test common package
cd helpcenter-common
pytest

# Test GraphQL API
cd helpcenter-graphql-api
pytest

# Test Editor API
cd helpcenter-editor-api
pytest
```

## Deployment

### Manual Deployment

```bash
# Deploy GraphQL API to Cloud Run
cd helpcenter-graphql-api
gcloud run deploy helpcenter-graphql-api --source .

# Deploy Editor API to Cloud Function
cd helpcenter-editor-api
./deploy-cloud-function.sh production
```

### CI/CD

The `separated-ci.yaml` workflow handles:
1. Testing all services
2. Building Docker images
3. Deploying to Cloud Run (GraphQL) and Cloud Function (Editor)

## Environment Variables

### GraphQL API
- `DATABASE_URL_ASYNC`
- `REDIS_URL`
- `SECRET_KEY`
- `GCS_BUCKET_NAME`
- `ALLOWED_ORIGINS`

### Editor API
- All GraphQL API variables plus:
- `DEV_EDITOR_KEY`

## Benefits of Separation

1. **Security**: Editor API is private, GraphQL API is public
2. **Scaling**: Independent scaling of services
3. **Cost**: Cloud Function only runs when needed
4. **Maintenance**: Clear separation of concerns
5. **Deployment**: Independent deployments

## Next Steps (Phase 2)

1. Add observability (Prometheus, Loki)
2. Implement health checks and alerts
3. Add rate limiting to editor endpoints
4. Create frontend for editor operations
