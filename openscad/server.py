import os
import re
import contextlib
import logging
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Image as MCPImage
from mcp_image_utils import to_mcp_image
import subprocess
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP using MCP_NAME (env) for tool name and base path
# Ensure the streamable path ends with '/'
MCP_NAME = os.getenv("MCP_NAME", "openscad")
_safe_name = re.sub(r"[^a-z0-9_-]", "-", MCP_NAME.lower()).strip("-") or "service"
BASE_PATH = f"/{_safe_name}"
STREAM_PATH = f"{BASE_PATH}/"
ENV_PREFIX = re.sub(r"[^A-Z0-9_]", "_", _safe_name.upper())
logger.info(f"Safe service name: {_safe_name}")
logger.info(f"Stream path: {STREAM_PATH}")

mcp = FastMCP(_safe_name, streamable_http_path=STREAM_PATH, json_response=True)

@mcp.tool()
def render_scad_script(scad_code: str, filename: str = "current", view: str = "3d", image_size: str = "800,600") -> MCPImage:
    """
    Render an OpenSCAD script to an image and return it as an MCP image.
    
    Args:
        scad_code (str): The OpenSCAD script code to render
        filename (str): Base filename for saving files (default: 'current' for real-time monitoring)
        view (str): The view to render - options: '3d', 'top', 'front', 'left' (default: '3d')
        image_size (str): Image size in format 'width,height' (default: '800,600')
    
    Returns:
        MCPImage: The rendered image in MCP format.
    """
    try:
        from PIL import Image as PILImage
        import shutil
        
        # Create data directories if they don't exist
        os.makedirs("./data/scad", exist_ok=True)
        os.makedirs("./data/render", exist_ok=True)
        
        # Create temporary files with specified filename
        temp_dir = tempfile.gettempdir()
        temp_scad_path = os.path.join(temp_dir, f"{filename}.scad")
        temp_png_path = os.path.join(temp_dir, f"{filename}.png")
        
        # Permanent file paths in organized directories (same filename each time for real-time monitoring)
        permanent_scad_path = f"./data/scad/{filename}.scad"
        permanent_png_path = f"./data/render/{filename}_{view}.png"
        
        # Write the SCAD code to file
        with open(temp_scad_path, 'w') as scad_file:
            scad_file.write(scad_code)
        
        try:
            # Define camera settings for different views
            camera_settings = {
                'top': ('0,0,100,0,0,0', 'ortho'),         # Looking down from above
                'front': ('0,-100,0,0,0,0', 'ortho'),      # Looking from front
                'left': ('-100,0,0,0,0,0', 'ortho'),       # Looking from left side
                '3d': ('70,70,50,0,0,0', 'perspective')    # Isometric view
            }
            
            if view not in camera_settings:
                raise ValueError(f"Invalid view '{view}'. Valid options: {list(camera_settings.keys())}")
            
            camera, projection = camera_settings[view]
            
            # Build OpenSCAD command
            cmd = [
                'openscad',
                '-o', temp_png_path,
                '--autocenter',
                '--viewall',
                f'--imgsize={image_size}',
                '--camera', camera,
                '--projection', projection,
                temp_scad_path
            ]
            
            # Run OpenSCAD
            logger.info(f"Running OpenSCAD command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise RuntimeError(f"OpenSCAD rendering failed: {result.stderr}")
            
            # Check if output file was created
            if not os.path.exists(temp_png_path):
                raise RuntimeError("OpenSCAD rendering succeeded but no output file was created")
            
            # Copy files to organized directories for permanent storage
            shutil.copy2(temp_scad_path, permanent_scad_path)
            shutil.copy2(temp_png_path, permanent_png_path)
            
            logger.info(f"Files saved: {permanent_scad_path}, {permanent_png_path}")
            
            # Load and return the image
            img = PILImage.open(temp_png_path)
            mcp_img = to_mcp_image(img, format='png')
            return mcp_img
            
        finally:
            # Clean up temporary files
            if os.path.exists(temp_scad_path):
                os.remove(temp_scad_path)
            if os.path.exists(temp_png_path):
                os.remove(temp_png_path)
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("OpenSCAD rendering timed out (30 seconds)")
    except Exception as e:
        logger.error(f"Exception occurred while rendering OpenSCAD script: {str(e)}")
        raise RuntimeError(f"Exception occurred while rendering OpenSCAD script: {str(e)}")

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
