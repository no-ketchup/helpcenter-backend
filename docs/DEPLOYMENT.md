# Google Cloud Deployment Guide

This guide covers deploying the Help Center Backend to Google Cloud Run with Google Cloud Storage.

## Prerequisites

1. **Google Cloud Account**: Sign up at [cloud.google.com](https://cloud.google.com)
2. **gcloud CLI**: Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
3. **Neon DB Account**: For PostgreSQL database
4. **GitHub Repository**: For CI/CD

## Setup Steps

### 1. Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Cloud Storage API
gcloud services enable storage.googleapis.com

# Enable Cloud Build API (for CI/CD)
gcloud services enable cloudbuild.googleapis.com
```

### 2. Create Google Cloud Storage Bucket

```bash
# Create bucket for media storage
gsutil mb gs://your-helpcenter-bucket

# Make bucket publicly readable (for media URLs)
gsutil iam ch allUsers:objectViewer gs://your-helpcenter-bucket
```

### 3. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create helpcenter-backend \
    --display-name="Help Center Backend"

# Grant Cloud Storage permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:helpcenter-backend@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Create and download key
gcloud iam service-accounts keys create service-account.json \
    --iam-account=helpcenter-backend@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 4. Set Environment Variables

Create a `.env.prod` file:

```bash
# Database
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/helpcenter?sslmode=require

# Google Cloud Storage
GCS_BUCKET_NAME=your-helpcenter-bucket
GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json

# Application
ENVIRONMENT=production
SECRET_KEY=your-production-secret-key
DEV_EDITOR_KEY=your-production-editor-key

# CORS
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### 5. Deploy to Cloud Run

#### Option A: Direct Deployment

```bash
# Deploy directly from source
gcloud run deploy helpcenter-backend \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars ENVIRONMENT=production \
    --set-env-vars GCS_BUCKET_NAME=your-helpcenter-bucket
```

#### Option B: Using Cloud Build

```bash
# Submit build
gcloud builds submit --config cloudbuild.yaml

# Deploy with environment variables
gcloud run deploy helpcenter-backend \
    --image gcr.io/YOUR_PROJECT_ID/helpcenter-backend:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars-from-file .env.prod
```

### 6. Set Up CI/CD with GitHub Actions

1. **Add Secrets to GitHub**:
   - `GCP_PROJECT_ID`: Your Google Cloud project ID
   - `GCP_SA_KEY`: Contents of your service-account.json file
   - `DATABASE_URL`: Your Neon DB connection string
   - `SECRET_KEY`: Production secret key
   - `DEV_EDITOR_KEY`: Production editor key

2. **Update GitHub Actions** (`.github/workflows/ci.yml`):
   ```yaml
   - name: Deploy to Cloud Run
     uses: google-github-actions/deploy-cloudrun@v1
     with:
       service: helpcenter-backend
       region: us-central1
       project_id: ${{ secrets.GCP_PROJECT_ID }}
       credentials: ${{ secrets.GCP_SA_KEY }}
   ```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Neon DB connection string | Yes |
| `GCS_BUCKET_NAME` | Google Cloud Storage bucket name | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON | Yes |
| `SECRET_KEY` | Application secret key | Yes |
| `DEV_EDITOR_KEY` | Dev editor authentication | Yes |
| `ENVIRONMENT` | Environment (production) | No |
| `ALLOWED_ORIGINS` | CORS allowed origins | No |

## Free Tier Limits

### Google Cloud Run
- **2M requests/month** free
- **400K vCPU-seconds/month** free
- **800K GiB-seconds/month** free
- **Auto-scaling to zero** when not in use

### Google Cloud Storage
- **5GB storage** free
- **1GB download/month** free
- **No time limits** on free tier

### Neon DB
- **3GB storage** free
- **10GB transfer/month** free
- **No time limits** on free tier

## Monitoring

### Cloud Run Metrics
- View in Google Cloud Console > Cloud Run
- Monitor requests, latency, and errors
- Set up alerts for high error rates

### Cloud Storage Metrics
- View in Google Cloud Console > Cloud Storage
- Monitor storage usage and requests

### Application Logs
```bash
# View logs
gcloud logs read --service=helpcenter-backend --limit=50

# Follow logs
gcloud logs tail --service=helpcenter-backend
```

## Troubleshooting

### Common Issues

1. **Service Account Permissions**:
   ```bash
   # Verify permissions
   gcloud projects get-iam-policy YOUR_PROJECT_ID
   ```

2. **CORS Issues**:
   - Check `ALLOWED_ORIGINS` environment variable
   - Ensure frontend URL is included

3. **Database Connection**:
   - Verify `DATABASE_URL` is correct
   - Check Neon DB connection limits

4. **Storage Access**:
   - Verify bucket exists and is accessible
   - Check service account has proper permissions

### Health Checks

```bash
# Test health endpoint
curl https://your-service-url.run.app/health

# Test GraphQL endpoint
curl -X POST https://your-service-url.run.app/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ categories { id name } }"}'
```

## Cost Optimization

1. **Use Cloud Run**: Pay only for actual usage
2. **Optimize Images**: Use appropriate image sizes
3. **Monitor Usage**: Set up billing alerts
4. **Use CDN**: Consider Cloud CDN for static assets

## Security

1. **Service Account**: Use least privilege principle
2. **Environment Variables**: Never commit secrets
3. **HTTPS**: Cloud Run provides HTTPS by default
4. **CORS**: Restrict allowed origins
5. **Database**: Use SSL connections (sslmode=require)
