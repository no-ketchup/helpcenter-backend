#!/bin/bash
set -euo pipefail

# Deploy Editor API to Cloud Run (not Cloud Function)
# Usage: ./scripts/deploy-editor.sh [environment] [github_sha]

ENVIRONMENT=${1:-staging}
GITHUB_SHA=${2:-latest}

echo "Deploying Editor API to Cloud Run..."

# Validate required environment variables
: "${GOOGLE_CLOUD_PROJECT:?ERROR: GOOGLE_CLOUD_PROJECT is not set}"
: "${GOOGLE_CLOUD_REGION:?ERROR: GOOGLE_CLOUD_REGION is not set}"
: "${NEON_DB_CONNECTION_STRING:?ERROR: NEON_DB_CONNECTION_STRING is not set}"
: "${REDIS_URL:?ERROR: REDIS_URL is not set}"
: "${SECRET_KEY:?ERROR: SECRET_KEY is not set}"
: "${DEV_EDITOR_KEY:?ERROR: DEV_EDITOR_KEY is not set}"
: "${GCS_BUCKET_NAME:?ERROR: GCS_BUCKET_NAME is not set}"
: "${HELPCENTER_GCS:?ERROR: HELPCENTER_GCS is not set}"
: "${ALLOWED_ORIGINS:?ERROR: ALLOWED_ORIGINS is not set}"

PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
REGION=${GOOGLE_CLOUD_REGION}
SERVICE_NAME="helpcenter-editor-api-${ENVIRONMENT}"
IMAGE_NAME="helpcenter-editor-api"

echo "Building Docker image for Editor API..."
docker build \
    -f editor_api/Dockerfile.uv \
    -t "gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${GITHUB_SHA}" \
    -t "gcr.io/${PROJECT_ID}/${IMAGE_NAME}:latest" \
    --build-arg "ENVIRONMENT=${ENVIRONMENT}" \
    .

echo "Configuring Docker for GCR..."
gcloud auth configure-docker --quiet

echo "Pushing Docker image..."
docker push "gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${GITHUB_SHA}"
docker push "gcr.io/${PROJECT_ID}/${IMAGE_NAME}:latest"

echo "Deploying to Cloud Run..."

python3 << 'PYTHON_EOF'
import yaml
import os

env_vars = {
    'ENVIRONMENT': os.environ.get('ENVIRONMENT', ''),
    'NEON_DB_CONNECTION_STRING': os.environ.get('NEON_DB_CONNECTION_STRING', ''),
    'REDIS_URL': os.environ.get('REDIS_URL', ''),
    'SECRET_KEY': os.environ.get('SECRET_KEY', ''),
    'DEV_EDITOR_KEY': os.environ.get('DEV_EDITOR_KEY', ''),
    'GCS_BUCKET_NAME': os.environ.get('GCS_BUCKET_NAME', ''),
    'HELPCENTER_GCS': os.environ.get('HELPCENTER_GCS', ''),
    'ALLOWED_ORIGINS': os.environ.get('ALLOWED_ORIGINS', ''),
}

with open('/tmp/env-vars.yaml', 'w') as f:
    yaml.dump(env_vars, f, default_flow_style=False, allow_unicode=True)
PYTHON_EOF

gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${GITHUB_SHA} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --service-account=helpcenter-runtime@${PROJECT_ID}.iam.gserviceaccount.com \
  --env-vars-file=/tmp/env-vars.yaml \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --concurrency 100

rm -f /tmp/env-vars.yaml

echo "Editor API deployment completed successfully!"
echo "Service URL: https://${SERVICE_NAME}-${REGION}.run.app"

