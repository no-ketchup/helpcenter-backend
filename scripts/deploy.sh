#!/bin/bash

# Help Center Backend Deployment Script
set -e

echo "Starting deployment..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found. Are you in the right directory?"
    exit 1
fi

# Check environment
if [ -z "$ENVIRONMENT" ]; then
    echo "Error: ENVIRONMENT variable not set"
    exit 1
fi

echo "Environment: $ENVIRONMENT"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Run tests
echo "Running tests..."
pytest tests/ -v

# Build Docker image
echo "Building Docker image..."
docker build -t helpcenter-backend:$ENVIRONMENT .

# Test Docker image
echo "Testing Docker image..."
docker run --rm -d --name test-container -p 8000:8000 helpcenter-backend:$ENVIRONMENT
sleep 10
curl -f http://localhost:8000/health || (echo "Health check failed" && exit 1)
docker stop test-container

echo "Deployment successful!"
echo "Help Center Backend is ready for $ENVIRONMENT"
