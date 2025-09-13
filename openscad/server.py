import os
import re
import json
import glob
import contextlib
import logging
import uvicorn
import requests
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP using MCP_NAME (env) for tool name and base path
# Ensure the streamable path ends with '/'
MCP_NAME = os.getenv("MCP_NAME", "openscad")
_safe_name = re.sub(r"[^a-z0-9_-]", "-", MCP_NAME.lower()).strip("-") or "service"
BASE_PATH = f"/{_safe_name}"
STREAM_PATH = f"{BASE_PATH}/"
ENV_PREFIX = re.sub(r"[^A-Z0-9_]", "_", _safe_name.upper())

mcp = FastMCP(_safe_name, streamable_http_path=STREAM_PATH, json_response=True)


# def _env_debug() -> bool:
#     return os.getenv("DEBUG", "").lower() in ("true", "1", "yes")


# def _env_limit() -> int:
#     try:
#         return int(os.getenv("LIMIT_PER_ENDPOINT", "1000"))
#     except Exception:
#         return 1000


# def _load_endpoint_descriptions() -> dict:
#     """Load endpoint descriptions from cbonds_api_field_descriptor.json if present."""
#     try:
#         path = "cbonds_api_field_descriptor.json"
#         if not os.path.exists(path):
#             logger.warning("cbonds_api_field_descriptor not found; using default tool descriptions")
#             return {}
#         with open(path, "r", encoding="utf-8") as f:
#             data = json.load(f) or {}
#             logger.info("Loaded endpoint descriptions from cbonds_api_field_descriptor for %d endpoints", len(data))
#             return {str(k): str(v) for k, v in data.items() if v is not None}
#     except Exception:
#         logger.exception("Failed to load cbonds_api_field_descriptor")
#         return {}


# @mcp.tool()
# def search(query: str) -> str:
#     """Empty stub for MCP 'search' tool; not used in this server."""
#     return json.dumps({"results": []})


# @mcp.tool()
# def fetch(id: str) -> str:
#     """Empty stub for MCP 'fetch' tool; not used in this server."""
#     return json.dumps({})


# # Dynamically register a dedicated MCP tool for each active cbonds endpoint
# def _register_endpoint_tools():
#     endpoints = ImprovedCbondsFetcher.ENDPOINTS or {}
#     descriptions = _load_endpoint_descriptions()

#     for endpoint_name in endpoints.keys():
#         tool_name = endpoint_name  # expose tools with the same name as endpoint
#         logger.info("Registering MCP tool for cbonds endpoint: %s", endpoint_name)

#         def _make_tool(ep: str, tool_label: str, desc_map: dict):
#             # Prepare a description to use as the tool docstring
#             default_desc = (
#                 f"Fetch data from cbonds endpoint '{ep}'. Accepts an ISIN. "
#                 f"If the result is a table (list of rows), returns only the first 10 rows."
#             )
#             description = desc_map.get(ep) or default_desc
#             logger.info("Tool '%s' description: %s", tool_label, description)

#             def endpoint_tool(isin: str) -> list[dict] | dict:
#                 try:
#                     fetcher = ImprovedCbondsFetcher(output_folder=os.getenv("OUTPUT_FOLDER", "output"))
#                     result = fetcher.fetch_specific_endpoint_data(
#                         [str(isin).strip()],
#                         endpoint_name=ep,
#                         debug=_env_debug(),
#                         limit_per_endpoint=_env_limit(),
#                     )

#                     # Extract the table-like items for the requested ISIN and endpoint
#                     items = (
#                         ((result or {}).get("isin_results", {})
#                          .get(str(isin).strip(), {})
#                          .get("endpoints", {})
#                          .get(ep, {})
#                          .get("data", {}) or {})
#                     ).get("items")

#                     if isinstance(items, list):
#                         return items[:10]
#                     return items if items is not None else (result or {})
#                 except Exception as e:
#                     logger.exception("Endpoint tool '%s' failed", ep)
#                     return {"error": str(e), "endpoint": ep, "isin": isin}

#             # Set docstring before decorating so FastMCP picks it up as tool description
#             endpoint_tool.__doc__ = description
#             endpoint_tool.__name__ = f"tool_{tool_label}"

#             decorated = mcp.tool(name=tool_label)(endpoint_tool)
#             globals()[endpoint_tool.__name__] = decorated

#         _make_tool(endpoint_name, tool_name, descriptions)
#         logger.info("Registered MCP tool: %s", tool_name)


# # Register endpoint tools at import time
# _register_endpoint_tools()

@mcp.tool()
def test(query: str) -> str:
    """Empty stub for MCP 'test' tool."""
    return json.dumps({"results": []})

# Build the main ASGI app with Streamable HTTP mounted
mcp_asgi = mcp.streamable_http_app()

@contextlib.asynccontextmanager
async def lifespan(_: Starlette):
    # Ensure FastMCP session manager is running, as required by Streamable HTTP
    async with mcp.session_manager.run():
        yield

app = Starlette(
    routes=[
        # Mount at root; internal app handles service path routing
        Mount("/", app=mcp_asgi),
    ],
    lifespan=lifespan,
)


class TokenAuthMiddleware(BaseHTTPMiddleware):
    """Simple token gate for all service requests under BASE_PATH.

    Accepts tokens via Authorization header: "Bearer <token>" (default and recommended).
    If env {ENV_PREFIX}_ALLOW_URL_TOKENS=true, also accepts:
      - Query parameter: ?token=<token>
      - URL path form: {BASE_PATH}/<token>/... (token is stripped before forwarding)

    Configure allowed tokens via env var {ENV_PREFIX}_TOKENS (comma-separated). If unset or empty,
    authentication is disabled (allows all) but logs a warning.
    """

    def __init__(self, app):
        super().__init__(app)
        # Prefer envs derived from MCP_NAME; fall back to legacy CBONDS_* names for backward compatibility
        raw = os.getenv(f"MCP_TOKENS", "")
        self.allowed_tokens = {t.strip() for t in raw.split(",") if t.strip()}
        self.allow_url_tokens = (
            os.getenv(f"MCP_ALLOW_URL_TOKENS", "").lower()
            in ("1", "true", "yes")
        )
        self.require_auth = (
            os.getenv(f"MCP_REQUIRE_AUTH", "").lower()
            in ("1", "true", "yes")
        )
        if not self.allowed_tokens:
            if self.require_auth:
                logger.warning(
                    "%s is not set; %s=true -> all %s requests will be rejected (401)",
                    f"MCP_TOKENS",
                    f"MCP_REQUIRE_AUTH",
                    BASE_PATH,
                )
            else:
                logger.warning(
                    "%s is not set; token auth is DISABLED for %s endpoints",
                    f"MCP_TOKENS",
                    BASE_PATH,
                )

    async def dispatch(self, request, call_next):
        # Only protect BASE_PATH path space
        path = request.url.path or "/"
        if not path.startswith(BASE_PATH):
            return await call_next(request)

        # If no tokens configured
        if not self.allowed_tokens:
            if self.require_auth:
                return JSONResponse({"detail": "Unauthorized"}, status_code=401, headers={"WWW-Authenticate": "Bearer"})
            return await call_next(request)

        # Authorization: Bearer <token>
        token = None
        auth = request.headers.get("authorization") or request.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1].strip()

        # Header token valid -> allow
        if token and token in self.allowed_tokens:
            return await call_next(request)

        # If URL tokens are allowed, check query and path variants
        if self.allow_url_tokens:
            # 1) Query parameter ?token=...
            url_token = request.query_params.get("token")
            if url_token and url_token in self.allowed_tokens:
                return await call_next(request)

            # 2) Path segment /<service>/<token>/...
            segs = [s for s in path.split("/") if s != ""]
            if len(segs) >= 2 and segs[0] == _safe_name:
                candidate = segs[1]
                if candidate in self.allowed_tokens:
                    # Rebuild path without the token segment
                    remainder = "/".join([_safe_name] + segs[2:])
                    new_path = "/" + (remainder + "/" if path.endswith("/") and not remainder.endswith("/") else remainder)
                    if new_path == BASE_PATH:
                        new_path = STREAM_PATH
                    request.scope["path"] = new_path
                    if "raw_path" in request.scope:
                        request.scope["raw_path"] = new_path.encode("utf-8")
                    return await call_next(request)

        # If we reached here, reject unauthorized
        if self.allow_url_tokens:
            detail = "Unauthorized"
        else:
            detail = "Use Authorization: Bearer <token>; URL/query tokens are not allowed"
        return JSONResponse({"detail": detail}, status_code=401, headers={"WWW-Authenticate": "Bearer"})


# Install auth middleware last to wrap the full app
app.add_middleware(TokenAuthMiddleware)

def main():
    """
    Run the uvicorn server without SSL (TLS handled by Caddy).
    """
    PORT = int(os.getenv("PORT", "8003"))

    logger.info(f"Starting {MCP_NAME} MCP server (HTTP) on port {PORT} at {STREAM_PATH}")

    uvicorn.run(
        app=app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=PORT,
        log_level=os.getenv("LOG_LEVEL", "info"),
        access_log=True,
        # Behind Caddy: respect X-Forwarded-* and use https in redirects
        proxy_headers=True,
        forwarded_allow_ips="*",
        timeout_keep_alive=75,
    )

if __name__ == "__main__":
    main()
