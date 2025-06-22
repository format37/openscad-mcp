# openscad-mcp
The openscad MCP server to compose openscad scripts and render them by LLM
# Claude desktop config
```
"openscad": {
        "command": "npx",
        "args": [
          "mcp-remote",
          "http://localhost:8000/sse"
        ],
        "disabled": false
      }
```