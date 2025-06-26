#!/bin/bash
set -e

echo "🚀 Starting Docker deployment..."

APP_NAME=tarafirst
APP_DIR=/home/ubuntu/tarafirst
ENV_FILE=/home/ubuntu/.env

cd $APP_DIR

echo "🛑 Stopping existing Docker container (if running)..."
sudo docker stop $APP_NAME || true
sudo docker rm $APP_NAME || true

echo "🐳 Building Docker image..."
sudo docker build -t $APP_NAME .

echo "🚀 Running Docker container..."
sudo docker run -d \
  --env-file $ENV_FILE \
  -p 8001:8000 \
  --restart on-failure:3 \
  --name $APP_NAME \
  $APP_NAME


echo "✅ Deployment complete! App '$APP_NAME' is now running."
