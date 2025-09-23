# Neon DB Setup (Free Tier)

## Step 1: Create Neon Account
1. Go to [neon.tech](https://neon.tech)
2. Sign up with GitHub
3. Create a new project
4. Copy the connection string

## Step 2: Update Environment
```bash
# In .env.local
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/helpcenter?sslmode=require
```

## Step 3: Test Connection
```bash
# Test database connection
make migrate

# Run tests
make test
```

## Step 4: Deploy Schema
```bash
# Apply migrations to Neon DB
make migrate
```

## Benefits
- ✅ 3GB storage free
- ✅ 10GB transfer/month free
- ✅ No time limits
- ✅ Serverless (scales to zero)
- ✅ No compute costs

## Next Steps
Once Neon DB is working, you can:
1. Test your frontend with real database
2. Decide if you want to deploy backend to Cloud Run
3. Set up GCS for media storage
