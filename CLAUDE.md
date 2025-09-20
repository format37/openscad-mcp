# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an OpenSCAD MCP (Model Context Protocol) server that enables LLMs to compose and render OpenSCAD scripts. The project is containerized and designed for production deployment with authentication and SSL termination.

## Architecture

### Project Structure
```
├── openscad/               # Core MCP server implementation
│   ├── server.py          # FastMCP server with OpenSCAD tools
│   ├── mcp_image_utils.py # Image processing utilities
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile        # Container with OpenSCAD + Xvfb
│   ├── CLAUDE.md         # Detailed implementation guidance
│   └── README.md         # Service-specific README
├── docker-compose.production.yml  # Production deployment config
├── production.sh         # Production deployment script
├── .env.production       # Environment configuration (not tracked)
├── Caddyfile            # SSL/proxy configuration
└── README.md            # Main setup instructions
```

### Core Components

**MCP Server** (`openscad/server.py`):
- FastMCP-based server exposing OpenSCAD rendering tools
- Two main tools: `render_scad_script` and `generate_stl`
- Token-based authentication with multiple auth methods
- File persistence with public URL generation
- Sentry integration for error tracking

**Container Environment** (`openscad/Dockerfile`):
- Python 3.11 base with OpenSCAD binary
- Xvfb for headless rendering
- Custom OpenSCAD wrapper for display management

## Development Commands

### Local Development
```bash
cd openscad
pip install -r requirements.txt
python server.py
```

### Production Deployment
```bash
# Configure environment variables in .env.production
./production.sh
```

### Container Operations
```bash
# Build container
cd openscad && docker build -t openscad-mcp .

# Run container locally
docker run -p 8004:8004 -e MCP_TOKENS=your_token openscad-mcp

# Check logs
docker logs mcp-openscad
```

## Environment Configuration

Key environment variables (configured in `.env.production`):

**Authentication**:
- `MCP_TOKENS`: Comma-separated list of valid tokens
- `MCP_REQUIRE_AUTH`: Set to `true` to enforce authentication
- `MCP_ALLOW_URL_TOKENS`: Allow tokens in URL paths/query params

**URLs**:
- `MCP_PUBLIC_BASE_URL`: Base URL for public asset access
- `MCP_PUBLIC_ASSET_BASE_URL`: Optional specific asset base URL
- `MCP_PUBLIC_LINK_TOKEN`: Token for public asset URLs

**Monitoring**:
- `SENTRY_DSN`: Sentry project DSN for error tracking

**Performance**:
- `RENDER_MAX_CONCURRENCY`: Max simultaneous renders (default: 2)
- `PORT`: Server port (default: 8004)

## MCP Tools

### render_scad_script(scad_code, view="3d")
Renders OpenSCAD scripts to preview images with download links
- **Views**: 3d, top, front, left
- **Output**: Preview image + public download URL
- **Timeout**: 30 seconds

### generate_stl(scad_code)
Generates STL files from OpenSCAD scripts for 3D printing
- **Output**: STL resource URI + public download URL
- **Timeout**: 60 seconds

## File Persistence

All generated files are stored persistently:
- **SCAD scripts**: `./data/scad/<uid>/`
- **Rendered images**: `./data/render/<uid>/`
- **STL files**: `./data/stl/<uid>/`

Public URLs are generated when `MCP_PUBLIC_BASE_URL` is configured.

## Authentication Patterns

The server supports multiple authentication methods:
1. **Bearer token** (recommended): `Authorization: Bearer <token>`
2. **Query parameter**: `?token=<token>` (if enabled)
3. **Path token**: `/<service>/<token>/...` (if enabled)

## Deployment Architecture

Production deployment uses:
- **Docker Compose**: Container orchestration
- **Caddy**: SSL termination and reverse proxy
- **External network**: `mcp-shared` for service communication
- **Persistent volumes**: File storage across container restarts

## Error Monitoring

Sentry integration provides:
- Automatic error capture from `logger.error()` calls
- Tool call tracking with structured metadata
- Performance monitoring for render operations

## Common Operations

**Check service status**:
```bash
docker ps | grep mcp-openscad
```

**View logs**:
```bash
docker logs mcp-openscad -f
```

**Restart service**:
```bash
./production.sh
```

**Update configuration**:
1. Edit `.env.production`
2. Run `./production.sh` to redeploy