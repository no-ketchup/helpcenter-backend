#!/bin/bash
set -euo pipefail

# Cloud Function deployment script for Editor API
# Usage: ./deploy-cloud-function.sh [staging|production]

ENVIRONMENT=${1:-staging}

echo "Starting deployment for environment: ${ENVIRONMENT}"

# Validate required environment variables
: "${GOOGLE_CLOUD_PROJECT:?ERROR: GOOGLE_CLOUD_PROJECT is not set}"
: "${GOOGLE_CLOUD_REGION:?ERROR: GOOGLE_CLOUD_REGION is not set}"

PROJECT_ID=${GOOGLE_CLOUD_PROJECT}
REGION=${GOOGLE_CLOUD_REGION}
FUNCTION_NAME="helpcenter-editor-api-${ENVIRONMENT}"

echo "Deploying to Cloud Function: ${FUNCTION_NAME}"

# Deploy to Cloud Function
echo "Deploying to Cloud Function..."
gcloud functions deploy ${FUNCTION_NAME} \
  --gen2 \
  --runtime=python311 \
  --source=. \
  --entry-point=editor_api \
  --trigger=http \
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
  --memory=1Gi \
  --timeout=300s \
  --max-instances=10 \
  --region=${REGION}

echo "Deployment complete."
echo "Function URL: https://${REGION}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME}"
