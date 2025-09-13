#!/bin/bash

# Load environment variables
source .env.localhost

sudo docker stop cv-builder-backend cv-builder-frontend 2>/dev/null || true

# Remove container before recreating to avoid port conflicts
docker rm -f cv-builder-backend cv-builder-frontend 2>/dev/null || true

# Run docker-compose with the environment file
docker-compose -f docker-compose.localhost.yml --env-file .env.localhost up --build -d