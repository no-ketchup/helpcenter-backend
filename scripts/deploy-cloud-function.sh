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

# Create env vars file to handle special characters
cat > /tmp/env-vars.yaml << EOF
ENVIRONMENT: "${ENVIRONMENT}"
NEON_DB_CONNECTION_STRING: "${NEON_DB_CONNECTION_STRING}"
REDIS_URL: "${REDIS_URL}"
SECRET_KEY: "${SECRET_KEY}"
DEV_EDITOR_KEY: "${DEV_EDITOR_KEY}"
GCS_BUCKET_NAME: "${GCS_BUCKET_NAME}"
HELPCENTER_GCS: "${HELPCENTER_GCS}"
ALLOWED_ORIGINS: "${ALLOWED_ORIGINS}"
EOF

gcloud functions deploy ${FUNCTION_NAME} \
  --gen2 \
  --runtime=python311 \
  --source=. \
  --entry-point=editor_api \
  --trigger-http \
  --allow-unauthenticated \
  --service-account=helpcenter-runtime@${PROJECT_ID}.iam.gserviceaccount.com \
  --env-vars-file=/tmp/env-vars.yaml \
  --memory=1Gi \
  --timeout=300s \
  --max-instances=10 \
  --region=${REGION}

rm -f /tmp/env-vars.yaml

echo "Deployment complete."
echo "Function URL: https://${REGION}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME}"
