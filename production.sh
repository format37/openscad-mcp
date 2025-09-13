#!/bin/bash

# Load environment variables
source .env.production

sudo docker stop mcp-openscad-resource-server 2>/dev/null || true

sudo docker compose -f docker-compose.production.yml --env-file .env.production up --build -d