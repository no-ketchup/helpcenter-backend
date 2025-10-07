#!/bin/bash
set -euo pipefail

# Cloud Run deployment script for GraphQL API
# Usage: ./deploy-cloud-run.sh [staging|production] [image-tag]

ENVIRONMENT=${1:-staging}
IMAGE_TAG=${2:-latest}

echo "Starting deployment for environment: ${ENVIRONMENT}"

# Validate required environment variables
: "${GOOGLE_CLOUD_PROJECT:?ERROR: GOOGLE_CLOUD_PROJECT is not set}"
: "${GOOGLE_CLOUD_REGION:?ERROR: GOOGLE_CLOUD_REGION is not set}"

PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
REGION=${GOOGLE_CLOUD_REGION}
SERVICE_NAME="helpcenter-graphql-api-${ENVIRONMENT}"

echo "Deploying to Cloud Run: ${SERVICE_NAME}"

echo "Environment variables:"
echo "ENVIRONMENT: ${ENVIRONMENT}"
echo "IMAGE_TAG: ${IMAGE_TAG}"
echo "NEON_DB_CONNECTION_STRING: ${NEON_DB_CONNECTION_STRING:0:20}..." # Show first 20 chars only
echo "REDIS_URL: ${REDIS_URL:0:20}..."
echo "GCS_BUCKET_NAME: ${GCS_BUCKET_NAME}"

# Build and push Docker image first
echo "Building Docker image..."
docker build -f Dockerfile.uv \
  -t gcr.io/${PROJECT_ID}/helpcenter-graphql-api:${IMAGE_TAG} \
  -t gcr.io/${PROJECT_ID}/helpcenter-graphql-api:latest \
  --build-arg ENVIRONMENT=${ENVIRONMENT} \
  .

echo "Configuring Docker for GCR..."
gcloud auth configure-docker --quiet

echo "Pushing Docker image..."
docker push gcr.io/${PROJECT_ID}/helpcenter-graphql-api:${IMAGE_TAG}
docker push gcr.io/${PROJECT_ID}/helpcenter-graphql-api:latest

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image gcr.io/${PROJECT_ID}/helpcenter-graphql-api:${IMAGE_TAG} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --service-account=helpcenter-runtime@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-env-vars "ENVIRONMENT=${ENVIRONMENT}" \
  --set-env-vars "NEON_DB_CONNECTION_STRING=${NEON_DB_CONNECTION_STRING}" \
  --set-env-vars "REDIS_URL=${REDIS_URL}" \
  --set-env-vars "SECRET_KEY=${SECRET_KEY}" \
  --set-env-vars "DEV_EDITOR_KEY=${DEV_EDITOR_KEY}" \
  --set-env-vars "GCS_BUCKET_NAME=${GCS_BUCKET_NAME}" \
  --set-env-vars "HELPCENTER_GCS=${HELPCENTER_GCS}" \
  --set-env-vars "ALLOWED_ORIGINS=${ALLOWED_ORIGINS}" \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --concurrency 100

echo "Deployment complete!"
echo "Service URL: https://${SERVICE_NAME}-${REGION}.run.app"
