import contextlib
import contextvars
import datetime
import logging
import os
import re
import subprocess
import tempfile
import threading
import uuid
from pathlib import Path
from typing import Any

import sentry_sdk
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Image as MCPImage

from mcp_image_utils import to_mcp_image

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),  # This goes to Docker logs
#     ]
# )
logger = logging.getLogger(__name__)

# Initialize Sentry if DSN is provided
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    logger.info(f"Initializing Sentry with DSN: {sentry_dsn[:20]}... (truncated for security)")
    sentry_sdk.init(
        dsn=sentry_dsn,
        # Enable logs to be sent to Sentry
        enable_logs=True,
    )
    logger.info("Sentry initialized successfully")
else:
    logger.info("Sentry DSN not provided, running without Sentry")

MCP_TOKEN_CTX = contextvars.ContextVar("mcp_token", default=None)

# Initialize FastMCP using MCP_NAME (env) for tool name and base path
# Ensure the streamable path ends with '/'
MCP_NAME = os.getenv("MCP_NAME", "openscad")
_safe_name = re.sub(r"[^a-z0-9_-]", "-", MCP_NAME.lower()).strip("-") or "service"
BASE_PATH = f"/{_safe_name}"
STREAM_PATH = f"{BASE_PATH}/"
ENV_PREFIX = re.sub(r"[^A-Z0-9_]", "_", _safe_name.upper())
logger.info(f"Safe service name: {_safe_name}")
logger.info(f"Stream path: {STREAM_PATH}")


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning("Invalid %s=%r; using %s", name, value, default)
        return default


def _sanitize_filename(name: str) -> str:
    sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "-", name).strip("-.")
    return sanitized or "script"


# Storage layout and public asset configuration
DATA_DIR = Path(os.getenv("MCP_DATA_DIR", "./data")).resolve()
SCAD_DIR = DATA_DIR / "scad"
RENDER_DIR = DATA_DIR / "render"
STL_DIR = DATA_DIR / "stl"

for directory in (SCAD_DIR, RENDER_DIR, STL_DIR):
    directory.mkdir(parents=True, exist_ok=True)

ASSETS_ROUTE = f"{STREAM_PATH.rstrip('/')}/assets"
ASSETS_DIR = RENDER_DIR
STL_ASSETS_ROUTE = f"{STREAM_PATH.rstrip('/')}/stl"

PUBLIC_BASE_URL = os.getenv("MCP_PUBLIC_BASE_URL")
if PUBLIC_BASE_URL:
    PUBLIC_BASE_URL = PUBLIC_BASE_URL.rstrip("/")

PUBLIC_ASSET_BASE_URL = os.getenv("MCP_PUBLIC_ASSET_BASE_URL")
if PUBLIC_ASSET_BASE_URL:
    PUBLIC_ASSET_BASE_URL = PUBLIC_ASSET_BASE_URL.rstrip("/")
elif PUBLIC_BASE_URL:
    PUBLIC_ASSET_BASE_URL = f"{PUBLIC_BASE_URL}{ASSETS_ROUTE}"



# Preview sizing (keep inline responses <~1MB)
PREVIEW_MAX_WIDTH = _env_int("MCP_PREVIEW_MAX_WIDTH", 800)
PREVIEW_MAX_HEIGHT = _env_int("MCP_PREVIEW_MAX_HEIGHT", 600)
PREVIEW_FORMAT = os.getenv("MCP_PREVIEW_FORMAT", "jpeg").lower()
if PREVIEW_FORMAT not in {"jpeg", "jpg", "png", "webp"}:
    logger.warning("Unsupported MCP_PREVIEW_FORMAT=%s; defaulting to jpeg", PREVIEW_FORMAT)
    PREVIEW_FORMAT = "jpeg"
PREVIEW_JPEG_QUALITY = _env_int("MCP_PREVIEW_JPEG_QUALITY", 85)

mcp = FastMCP(_safe_name, streamable_http_path=STREAM_PATH, json_response=True)

# Add custom error handling for stream disconnections
original_logger = logging.getLogger("mcp.server.streamable_http")

class StreamErrorFilter(logging.Filter):
    def filter(self, record):
        # Suppress ClosedResourceError logs as they're expected when clients disconnect
        if "ClosedResourceError" in str(record.getMessage()):
            return False
        return True

original_logger.addFilter(StreamErrorFilter())

# Concurrency guard to prevent CPU/memory overload on weak hosts
_max_concurrency = _env_int("RENDER_MAX_CONCURRENCY", _env_int("OPENSCAD_MAX_CONCURRENCY", 2))
_render_semaphore = threading.Semaphore(_max_concurrency)







@mcp.tool()
def render_scad_script(
    scad_code: str,
    view: str = "3d",
) -> list[Any]:
    """Render an OpenSCAD script and return a preview image with download link.

    Generates a full-resolution PNG via OpenSCAD and returns a JPEG/PNG preview
    with an HTTPS URL for downloading the full-resolution image. Always provide
    the Preview URL to users for downloading the rendered image.
    """

    try:
        with _render_semaphore:
            from PIL import Image as PILImage
            import shutil

            logger.info("render_scad_script invoked")

            # Auto-generate UID and filename
            render_uid = str(uuid.uuid4())
            filename = f"render_{render_uid[:8]}"

            # Log tool call details
            logger.info(f"render_scad_script: view={view}, render_uid={render_uid}, scad_length={len(scad_code)}")
            uid_scad_dir = SCAD_DIR / render_uid
            uid_render_dir = RENDER_DIR / render_uid

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".scad", delete=False
            ) as scad_file:
                temp_scad_path = Path(scad_file.name)
                scad_file.write(scad_code)
            temp_png_fd, temp_png_path_str = tempfile.mkstemp(suffix=".png")
            os.close(temp_png_fd)
            temp_png_path = Path(temp_png_path_str)

            safe_base = _sanitize_filename(filename)
            png_name = f"{safe_base}_{view}.png"
            permanent_scad_path = uid_scad_dir / f"{safe_base}.scad"
            permanent_png_path = uid_render_dir / png_name

            try:
                camera_settings = {
                    "top": ("0,0,100,0,0,0", "ortho"),
                    "front": ("0,-100,0,0,0,0", "ortho"),
                    "left": ("-100,0,0,0,0,0", "ortho"),
                    "3d": ("70,70,50,0,0,0", "perspective"),
                }

                if view not in camera_settings:
                    raise ValueError(
                        f"Invalid view '{view}'. Valid options: {list(camera_settings.keys())}"
                    )

                camera, projection = camera_settings[view]

                cmd = [
                    "openscad",
                    "-o",
                    str(temp_png_path),
                    "--autocenter",
                    "--viewall",
                    "--imgsize=800,600",
                    "--camera",
                    camera,
                    "--projection",
                    projection,
                    str(temp_scad_path),
                ]

                logger.info("Running OpenSCAD command: %s", " ".join(cmd))
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=30
                )

                if result.returncode != 0:
                    raise RuntimeError(
                        f"OpenSCAD rendering failed: {result.stderr.strip()}"
                    )

                if not temp_png_path.exists():
                    raise RuntimeError(
                        "OpenSCAD rendering succeeded but no output file was created"
                    )

                # Always persist files
                uid_scad_dir.mkdir(parents=True, exist_ok=True)
                uid_render_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(temp_scad_path, permanent_scad_path)
                shutil.copy2(temp_png_path, permanent_png_path)
                logger.info(
                    "Persisted render UID=%s files at %s and %s",
                    render_uid,
                    permanent_scad_path,
                    permanent_png_path,
                )

                with PILImage.open(temp_png_path) as full_image:
                    preview_image = full_image.copy()
                    try:
                        resample = PILImage.Resampling.LANCZOS
                    except AttributeError:  # Pillow < 10 fallback
                        resample = PILImage.LANCZOS
                    preview_image.thumbnail(
                        (PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT), resample=resample
                    )

                preview_kwargs: dict[str, Any] = {}
                if PREVIEW_FORMAT in {"jpeg", "jpg"}:
                    preview_kwargs["quality"] = PREVIEW_JPEG_QUALITY
                    preview_kwargs["optimize"] = True
                elif PREVIEW_FORMAT in {"png", "webp"}:
                    preview_kwargs["optimize"] = True

                preview_block: MCPImage = to_mcp_image(
                    preview_image,
                    format=PREVIEW_FORMAT,
                    **preview_kwargs,
                )
                preview_content = preview_block.to_image_content()

                asset_relative_path = f"{render_uid}/{png_name}"
                public_url = None
                if PUBLIC_ASSET_BASE_URL:
                    public_url = f"{PUBLIC_ASSET_BASE_URL}/{asset_relative_path}"

                if public_url:
                    info_lines = [f"{public_url}"]
                else:
                    info_lines = ["Configure MCP_PUBLIC_BASE_URL or MCP_PUBLIC_ASSET_BASE_URL to expose HTTPS asset links."]

                # Log successful render
                logger.info(f"render_scad_script successful: {view} view rendered, render_uid={render_uid}, url={public_url or 'not_configured'}")

                return [preview_content, "\n".join(info_lines)]

            finally:
                if temp_scad_path.exists():
                    temp_scad_path.unlink()
                if temp_png_path.exists():
                    temp_png_path.unlink()

    except subprocess.TimeoutExpired as exc:
        logger.error(f"OpenSCAD rendering timed out: tool=render_scad_script, view={view}")
        raise RuntimeError("OpenSCAD rendering timed out (30 seconds)") from exc
    except Exception as exc:
        logger.error(f"Exception in render_scad_script: tool=render_scad_script, view={view}, error={exc}")
        raise RuntimeError(
            f"Exception occurred while rendering OpenSCAD script: {exc}"
        ) from exc


@mcp.tool()
def generate_stl(
    scad_code: str,
) -> list[Any]:
    """Generate an STL file from OpenSCAD code and provide download links.

    Takes OpenSCAD code and generates downloadable STL and SCAD files for 3D printing or CAD import.
    Returns HTTPS download URLs for both files. IMPORTANT: Always provide both STL and SCAD URLs to users so they
    can download the generated 3D model file for 3D printing or CAD software and the source code.
    """

    try:
        with _render_semaphore:
            import shutil

            logger.info("generate_stl invoked")

            # Auto-generate UID and filename
            stl_uid = str(uuid.uuid4())
            output_filename = f"model_{stl_uid[:8]}"
            uid_stl_dir = STL_DIR / stl_uid

            # Log tool call details
            logger.info(f"generate_stl: stl_uid={stl_uid}, output_filename={output_filename}, scad_length={len(scad_code)}")

            # Use provided scad_code directly
            scad_content = scad_code

            # Create temporary files
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".scad", delete=False
            ) as scad_file:
                temp_scad_path = Path(scad_file.name)
                scad_file.write(scad_content)

            temp_stl_fd, temp_stl_path_str = tempfile.mkstemp(suffix=".stl")
            os.close(temp_stl_fd)
            temp_stl_path = Path(temp_stl_path_str)

            safe_output_name = _sanitize_filename(output_filename)
            stl_filename = f"{safe_output_name}.stl"
            permanent_stl_path = uid_stl_dir / stl_filename

            try:
                # Generate STL using OpenSCAD
                cmd = [
                    "openscad",
                    "-o",
                    str(temp_stl_path),
                    str(temp_scad_path),
                ]

                logger.info("Running OpenSCAD STL command: %s", " ".join(cmd))
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=60
                )

                if result.returncode != 0:
                    raise RuntimeError(
                        f"OpenSCAD STL generation failed: {result.stderr.strip()}"
                    )

                if not temp_stl_path.exists():
                    raise RuntimeError(
                        "OpenSCAD STL generation succeeded but no output file was created"
                    )

                # Always persist STL and SCAD files
                uid_stl_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(temp_stl_path, permanent_stl_path)

                # Also save the SCAD file alongside the STL
                scad_filename = f"{safe_output_name}.scad"
                permanent_scad_path = uid_stl_dir / scad_filename
                shutil.copy2(temp_scad_path, permanent_scad_path)

                logger.info(
                    "Persisted STL UID=%s files at %s and %s",
                    stl_uid,
                    permanent_stl_path,
                    permanent_scad_path,
                )

                # Generate resource URI
                # stl_resource_uri = f"{_safe_name}://stl/{stl_uid}/{safe_output_name}.stl"

                # Get file size for info
                stl_size = temp_stl_path.stat().st_size

                # Generate public URLs for both STL and SCAD files
                stl_asset_relative_path = f"{stl_uid}/{stl_filename}"
                scad_asset_relative_path = f"{stl_uid}/{scad_filename}"

                stl_public_url = None
                scad_public_url = None
                if PUBLIC_BASE_URL:
                    stl_public_url = f"{PUBLIC_BASE_URL}{STL_ASSETS_ROUTE}/{stl_asset_relative_path}"
                    scad_public_url = f"{PUBLIC_BASE_URL}{STL_ASSETS_ROUTE}/{scad_asset_relative_path}"

                if stl_public_url and scad_public_url:
                    info_lines = [f"STL: {stl_public_url}", f"SCAD: {scad_public_url}"]
                else:
                    info_lines = ["Configure MCP_PUBLIC_BASE_URL to expose HTTPS STL and SCAD links."]

                # Log successful STL generation
                logger.info(f"generate_stl successful: {stl_filename} and {scad_filename} generated, stl_uid={stl_uid}, size={stl_size} bytes, stl_url={stl_public_url or 'not_configured'}, scad_url={scad_public_url or 'not_configured'}")

                # return [stl_resource_uri, "\n".join(info_lines)]
                return ["\n".join(info_lines)]

            finally:
                if temp_scad_path.exists():
                    temp_scad_path.unlink()
                if temp_stl_path.exists():
                    temp_stl_path.unlink()

    except subprocess.TimeoutExpired as exc:
        logger.error(f"OpenSCAD STL generation timed out: tool=generate_stl, stl_uid={stl_uid}")
        raise RuntimeError("OpenSCAD STL generation timed out (60 seconds)") from exc
    except Exception as exc:
        logger.error(f"Exception in generate_stl: tool=generate_stl, stl_uid={stl_uid}, error={exc}")
        raise RuntimeError(
            f"Exception occurred while generating STL: {exc}"
        ) from exc



@mcp.resource(f"{_safe_name}://render/{{uid}}/{{name}}_{{view}}.png", mime_type="image/png")
def get_render_resource(uid: str, name: str, view: str) -> bytes:
    """Expose persisted render PNGs as MCP resources."""

    safe_name = _sanitize_filename(name)
    path = RENDER_DIR / uid / f"{safe_name}_{view}.png"
    if not path.exists():
        raise FileNotFoundError(
            f"Render {uid}/{safe_name}_{view}.png not found on server"
        )
    return path.read_bytes()




@mcp.resource(f"{_safe_name}://source/{{uid}}/{{name}}.scad", mime_type="text/plain")
def get_scad_resource(uid: str, name: str) -> str:
    """Expose persisted SCAD sources as MCP resources."""

    safe_name = _sanitize_filename(name)
    path = SCAD_DIR / uid / f"{safe_name}.scad"
    if not path.exists():
        raise FileNotFoundError(
            f"Source {uid}/{safe_name}.scad not found on server"
        )
    return path.read_text()


@mcp.resource(f"{_safe_name}://stl/{{uid}}/{{name}}.stl", mime_type="model/stl")
def get_stl_resource(uid: str, name: str) -> bytes:
    """Expose persisted STL files as MCP resources."""

    safe_name = _sanitize_filename(name)
    path = STL_DIR / uid / f"{safe_name}.stl"
    if not path.exists():
        raise FileNotFoundError(
            f"STL {uid}/{safe_name}.stl not found on server"
        )
    return path.read_bytes()


@mcp.resource(
    f"{_safe_name}://documentation",
    name="OpenSCAD Documentation",
    description="Documentation and guidance for using OpenSCAD scripting language",
    mime_type="text/markdown"
)
def get_documentation_resource() -> str:
    """Expose OpenSCAD documentation as an MCP resource."""

    doc_path = Path("/app/openscad_documentation.md")
    if not doc_path.exists():
        raise FileNotFoundError("OpenSCAD documentation not found on server")
    return doc_path.read_text()

# Build the main ASGI app with Streamable HTTP mounted
mcp_asgi = mcp.streamable_http_app()

@contextlib.asynccontextmanager
async def lifespan(_: Starlette):
    # Ensure FastMCP session manager is running, as required by Streamable HTTP
    async with mcp.session_manager.run():
        yield

async def health_check(request):
    """Health endpoint for monitoring and load balancer checks."""
    try:
        # Check OpenSCAD availability
        openscad_available = True
        openscad_version = None
        try:
            result = subprocess.run(
                ["openscad", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                # Extract version from output
                version_line = result.stderr.strip() or result.stdout.strip()
                openscad_version = version_line.split('\n')[0] if version_line else "unknown"
            else:
                openscad_available = False
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            openscad_available = False

        # Check directory accessibility
        directories_ok = all(
            directory.exists() and directory.is_dir() 
            for directory in [DATA_DIR, SCAD_DIR, RENDER_DIR, STL_DIR]
        )

        # Check semaphore availability
        semaphore_available = _render_semaphore._value > 0

        # Determine overall status
        healthy = openscad_available and directories_ok
        status = "healthy" if healthy else "unhealthy"

        health_data = {
            "status": status,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "service": _safe_name,
            "version": "1.0.0",  # You can make this configurable
            "checks": {
                "openscad": {
                    "available": openscad_available,
                    "version": openscad_version
                },
                "directories": {
                    "accessible": directories_ok,
                    "data_dir": str(DATA_DIR),
                    "scad_dir": str(SCAD_DIR), 
                    "render_dir": str(RENDER_DIR),
                    "stl_dir": str(STL_DIR)
                },
                "concurrency": {
                    "available_slots": _render_semaphore._value,
                    "max_concurrent": _max_concurrency
                }
            }
        }

        status_code = 200 if healthy else 503
        return JSONResponse(health_data, status_code=status_code)

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }, status_code=503)


app = Starlette(
    routes=[
        Route("/health", health_check, methods=["GET"]),
        Route(f"{BASE_PATH}/health", health_check, methods=["GET"]),
        Mount(
            ASSETS_ROUTE,
            app=StaticFiles(directory=ASSETS_DIR, check_dir=False),
            name="assets",
        ),
        Mount(
            STL_ASSETS_ROUTE,
            app=StaticFiles(directory=STL_DIR, check_dir=False),
            name="stl_assets",
        ),
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
        # Only protect BASE_PATH path space, but allow public access to asset routes
        path = request.url.path or "/"
        if not path.startswith(BASE_PATH):
            return await call_next(request)

        # Allow public access to health endpoints, asset routes (they use UUID-based security)
        if (path in ["/health", f"{BASE_PATH}/health"] or 
            path.startswith(ASSETS_ROUTE) or 
            path.startswith(STL_ASSETS_ROUTE)):
            return await call_next(request)

        def accept(token_value: str, source: str):
            request.state.mcp_token = token_value  # stash for downstream use
            logger.info(
                "Authenticated %s %s via %s token %s",
                request.method,
                path,
                source,
                token_value,
            )
            return MCP_TOKEN_CTX.set(token_value)

        async def proceed(token_value: str, source: str):
            token_scope = accept(token_value, source)
            try:
                return await call_next(request)
            finally:
                MCP_TOKEN_CTX.reset(token_scope)

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
            return await proceed(token, "header")

        # If URL tokens are allowed, check query and path variants
        if self.allow_url_tokens:
            # 1) Query parameter ?token=...
            url_token = request.query_params.get("token")
            if url_token and url_token in self.allowed_tokens:
                return await proceed(url_token, "query")

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
                    return await proceed(candidate, "path")

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
        timeout_keep_alive=120,
    )

if __name__ == "__main__":
    main()
