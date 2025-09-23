#!/bin/bash
set -euo pipefail

# Cloud Run deployment script
# Usage: ./scripts/deploy-cloud-run.sh [staging|production]

ENVIRONMENT=${1:-staging}

echo "Starting deployment for environment: ${ENVIRONMENT}"

# Validate required environment variables
: "${GOOGLE_CLOUD_PROJECT:?ERROR: GOOGLE_CLOUD_PROJECT is not set}"
: "${GOOGLE_CLOUD_REGION:?ERROR: GOOGLE_CLOUD_REGION is not set}"

PROJECT_ID="${GOOGLE_CLOUD_PROJECT}"
REGION="${GOOGLE_CLOUD_REGION}"
SERVICE_NAME="helpcenter-backend-${ENVIRONMENT}"
TAG=${GITHUB_SHA:-latest}

echo "Deploying to Cloud Run: ${SERVICE_NAME} (image tag: ${TAG})"

# Build and push image
echo "Building and pushing Docker image..."
echo "Using PROJECT_ID: ${PROJECT_ID}"
echo "Using TAG: ${TAG}"
gcloud builds submit . --config cloudbuild.yaml --substitutions=_TAG=${TAG}

# Deploy to Cloud Run using the pre-built image
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/helpcenter-backend:${TAG} \
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
  --set-secrets=GOOGLE_APPLICATION_CREDENTIALS=GCS_SA_KEY:latest \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --concurrency 100

echo "Deployment complete!"
echo "Service URL: https://${SERVICE_NAME}-${REGION}.run.app"
