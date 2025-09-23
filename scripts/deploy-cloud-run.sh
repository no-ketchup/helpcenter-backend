#!/bin/bash
set -euo pipefail

# Cloud Run deployment script
# Usage: ./scripts/deploy-cloud-run.sh [staging|production]

ENVIRONMENT=${1:-staging}

echo "Starting deployment for environment: ${ENVIRONMENT}"

# Validate required environment variables
if [ -z "${GOOGLE_CLOUD_PROJECT:-}" ]; then
  echo "ERROR: GOOGLE_CLOUD_PROJECT is not set"
  exit 1
fi

if [ -z "${GOOGLE_CLOUD_REGION:-}" ]; then
  echo "ERROR: GOOGLE_CLOUD_REGION is not set"
  exit 1
fi

PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
REGION=${GOOGLE_CLOUD_REGION}
SERVICE_NAME="helpcenter-backend-${ENVIRONMENT}"

echo "Deploying to Cloud Run: ${SERVICE_NAME}"

# Build and push image
echo "Building and pushing Docker image..."
gcloud builds submit . --config cloudbuild.yaml

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/helpcenter-backend:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars "ENVIRONMENT=${ENVIRONMENT}" \
  --set-env-vars "DATABASE_URL_ASYNC=${DATABASE_URL_ASYNC}" \
  --set-env-vars "REDIS_URL=${REDIS_URL}" \
  --set-env-vars "SECRET_KEY=${SECRET_KEY}" \
  --set-env-vars "DEV_EDITOR_KEY=${DEV_EDITOR_KEY}" \
  --set-env-vars "GCS_BUCKET_NAME=${GCS_BUCKET_NAME}" \
  --set-env-vars "ALLOWED_ORIGINS=${ALLOWED_ORIGINS}" \
  --set-secrets "GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS_SECRET}:latest" \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --concurrency 100

echo "Deployment complete!"
echo "Service URL: https://${SERVICE_NAME}-${REGION}.run.app"
