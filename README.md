# OpenSCAD MCP
Openscad MCP server, that has the following features:
* openscad code rendering to png
* stl generation from openscad code
* openscad documentation resource
## Demo Video
Watch the OpenSCAD MCP in action:

[![OpenSCAD MCP Demo](https://img.youtube.com/vi/_wX1f8O_n8M/0.jpg)](https://youtu.be/_wX1f8O_n8M)

### Client side installation
Available in Claude web, Claude mobile, Chat GPT Web, and any other mcp client
```
https://rtlm.info/openscad/8TikTAffQT3Db65Q7xbofbUjapGjKepTI3sikOeLWClfXW5GXO/
```
*The provided url is defined for demonstration and would be removed eventually.*

## Server installation

### Requirements
* donaim name
* linux machine with ext ip
* sufficien firewall ports configuration

### 1. Reverse-proxy
Install [this](https://github.com/format37/reverse-proxy) or use your own.

### 2. Git clone
```bash
git clone https://github.com/format37/openscad-mcp.git
cd openscad-mcp
```

### 3. Environment variables
Localhost
```bash
cd mcp
nano .env.production
```
Generate any token.
Define: tokens divided by comma:
```
MCP_TOKENS=YOUR_TOKEN
MCP_REQUIRE_AUTH=true
MCP_ALLOW_URL_TOKENS=true
```

### 4. Compose
```bash
./production.sh
```

### Concurrency & Persistence
- The server limits simultaneous OpenSCAD renders with `RENDER_MAX_CONCURRENCY` (default: 2). Increase carefully on small hosts.
- Each render is saved under `./data/scad/<uid>/` and `./data/render/<uid>/` with filenames derived from the provided `filename` plus the view (e.g., `script_3d.png`). You can pass a custom `uid` if you need predictable locations.

### 5. Claude desktop config
The token is defined temporary for demo and may be unavailable later. Make ur own server)
```
{
  "mcpServers": {
      "openscad": {
        "command": "npx",
        "args": [
          "mcp-remote",
          "https://rtlm.info/openscad/8TikTAffQT3Db65Q7xbofbUjapGjKepTI3sikOeLWClfXW5GXO/"
        ]
    }
  }
}
```
