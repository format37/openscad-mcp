# OpenSCAD MCP

## Installation

### 1. SSL certificate generation
Update your subdomain name if required
```bash
sudo apt install certbot
sudo certbot certonly --standalone -d service.dnk-technologies.com
```
Auto-renewal setup:
```bash
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

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

# Define the Caddyfile
Need to define domain name in the first line. Subtomain is also acceptable.

### 4. Compose
```bash
./production.sh
```

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

### 6. Claude web & Claude mobile
Can be defined only in claude web.
```
https://rtlm.info/openscad/8TikTAffQT3Db65Q7xbofbUjapGjKepTI3sikOeLWClfXW5GXO/
```
Chat GPT requiring the search and fetch tools, which is non-sense for this server purpose.