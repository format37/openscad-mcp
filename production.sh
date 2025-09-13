#!/bin/bash

# Load environment variables
source .env.production

sudo docker stop cv-builder-backend cv-builder-frontend 2>/dev/null || true

# Remove container before recreating to avoid port conflicts
docker rm -f cv-builder-backend cv-builder-frontend 2>/dev/null || true

docker compose -f docker-compose.production.yml --env-file .env.production up --build -d