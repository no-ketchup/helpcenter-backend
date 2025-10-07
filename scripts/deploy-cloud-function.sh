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

echo "Deploying to Cloud Function..."

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
