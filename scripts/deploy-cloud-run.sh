#!/bin/bash
set -euo pipefail

# Cloud Run deployment script
# Usage: ./scripts/deploy-cloud-run.sh [staging|production]

ENVIRONMENT=${1:-staging}

echo "Starting deployment for environment: ${ENVIRONMENT}"

# Validate required environment variables
: "${GOOGLE_CLOUD_PROJECT:?ERROR: GOOGLE_CLOUD_PROJECT is not set}"
: "${GOOGLE_CLOUD_REGION:?ERROR: GOOGLE_CLOUD_REGION is not set}"

PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
REGION=${GOOGLE_CLOUD_REGION}
SERVICE_NAME="helpcenter-backend-${ENVIRONMENT}"

echo "Deploying to Cloud Run: ${SERVICE_NAME}"

# Debug: Show environment variables (without exposing sensitive data)
echo "Environment variables:"
echo "ENVIRONMENT: ${ENVIRONMENT}"
echo "DATABASE_URL_ASYNC: ${DATABASE_URL_ASYNC:0:20}..." # Show first 20 chars only
echo "REDIS_URL: ${REDIS_URL:0:20}..."
echo "GCS_BUCKET_NAME: ${GCS_BUCKET_NAME}"

# Note: Docker image is built and pushed by GitHub Actions
# No need to build here since GitHub Actions handles it

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/helpcenter-backend:${GITHUB_SHA:-latest} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --service-account=helpcenter-runtime@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-env-vars "ENVIRONMENT=${ENVIRONMENT}" \
  --set-env-vars "DATABASE_URL_ASYNC=${DATABASE_URL_ASYNC}" \
  --set-env-vars "REDIS_URL=${REDIS_URL}" \
  --set-env-vars "SECRET_KEY=${SECRET_KEY}" \
  --set-env-vars "DEV_EDITOR_KEY=${DEV_EDITOR_KEY}" \
  --set-env-vars "GCS_BUCKET_NAME=${GCS_BUCKET_NAME}" \
  --set-env-vars "ALLOWED_ORIGINS=${ALLOWED_ORIGINS}" \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --concurrency 100

echo "Deployment complete!"
echo "Service URL: https://${SERVICE_NAME}-${REGION}.run.app"
