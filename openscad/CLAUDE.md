# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is an OpenSCAD MCP (Model Context Protocol) server that allows LLMs to compose OpenSCAD scripts and render them. The server provides tools for script rendering and file management through the MCP protocol.

## Core Architecture

### Main Components
- **server.py**: FastMCP server implementation with two main MCP tools:
  - `render_scad_script`: Renders OpenSCAD scripts to images with various view options
  - `generate_stl`: Generates STL files from OpenSCAD scripts or existing SCAD files
- **mcp_image_utils.py**: Image processing utilities for PIL/MCP image conversion
- **Dockerfile**: Container setup with OpenSCAD and headless rendering (Xvfb)

### Key Functions
- `render_scad_script()` (server.py:124): Main rendering function that executes OpenSCAD with various parameters (3d, top, front, etc. views)
- `generate_stl()` (server.py:303): STL generation function that creates 3D model files from OpenSCAD scripts
- `to_mcp_image()` (mcp_image_utils.py:56): Converts PIL images to MCP format

### Data Flow
1. MCP client calls tools via FastMCP framework
2. OpenSCAD scripts are written to temporary files
3. OpenSCAD binary renders images or generates STL files using Xvfb (headless)
4. Generated files (images/STL) are processed and stored with unique identifiers
5. Resource URIs are returned for client access to generated files

## Development Commands

### Running the Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python server.py
```

### Docker Development
```bash
# Build container
docker build -t openscad-mcp .

# Run container
docker run -p 8004:8004 openscad-mcp
```

### Environment Configuration
- `MCP_NAME`: Service name (default: "openscad")
- `PORT`: Server port (default: 8004 in Docker, 8000 otherwise)
- `OPENSCAD_THREADS`: Concurrent rendering limit (default: 1)
- `MAX_FILE_SIZE`: Upload size limit (default: 100MB)

## OpenSCAD Integration
- Requires OpenSCAD binary in PATH
- Uses Xvfb for headless rendering in containerized environments
- **Image rendering**: Supports multiple view angles (3d, top, bottom, front, back, left, right) with configurable size
- **STL generation**: Creates 3D model files for 3D printing or CAD software import
- Configurable timeouts: 30s for image rendering, 60s for STL generation

## MCP Protocol Details
The server exposes tools via Server-Sent Events (SSE) endpoint at `/{service-name}/` and follows the FastMCP framework patterns. Authentication is handled via MCP token context variables.

## File Structure
```
├── server.py           # Main MCP server with rendering and STL tools
├── mcp_image_utils.py  # Image processing utilities
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container with OpenSCAD + Xvfb
└── README.md          # Basic setup instructions
```

## Tool Usage

### render_scad_script(scad_code, view="3d")
- **Input**: OpenSCAD code string, optional view angle
- **Output**: Preview image + resource links for full-resolution PNG
- **Views**: 3d (default), top, front, left, right
- **Always persists** files with auto-generated UIDs and filenames

### generate_stl(scad_code)
- **Input**: OpenSCAD code string
- **Output**: Resource URI + public HTTPS URL for STL download
- **Public URLs**: `{PUBLIC_BASE_URL}/openscad/stl/{uid}/{filename}.stl`
- **Always persists** files with auto-generated UIDs and filenames
- **Use cases**: 3D printing, CAD import, mesh processing

## Simplified Architecture
- **No complex parameters**: Only essential inputs (scad_code, optional view)
- **Auto-generated filenames**: No manual naming required
- **Always persistent**: All files are stored and accessible via URLs
- **No authentication noise**: Clean logging focused on operations