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
TOKENS=YOUR_TOKEN
REQUIRE_AUTH=true
ALLOW_URL_TOKENS=true
```

### 4. Compose
```bash
./production.sh
```