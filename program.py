from mcp.server.fastmcp import FastMCP
# from PIL import Image as PILImage
from mcp.server.fastmcp import Image as MCPImage
from mcp_image_utils import to_mcp_image
# from twitter_tools import get_topic_influencers_and_tweets, format_result_for_markdown
# from polygon import RESTClient
# from datetime import datetime, timedelta, UTC
import os
import traceback
import logging
import subprocess
import tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
# import requests
# import matplotlib.pyplot as plt
# import matplotlib.table as tbl
from typing import List, Dict, Any, Optional
import base64
import io
# import math
# import numpy as np
# import sympy as sp
# import pandas as pd
# import matplotlib.pyplot as plt
# import matplotlib.table as tbl
# from coinglass_tools import fetch_whale_positions, fetch_exchange_balance


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("Starting server")

mcp = FastMCP("openscad")

# @mcp.tool()
# def render() -> MCPImage:
#     """
#     Read the solid_render_3d.png file and return it as an MCP image.
    
#     Returns:
#         MCPImage: The solid_render_3d.png image in MCP format.
#     """
#     try:
#         from PIL import Image as PILImage
#         image_path = "solid_render_3d.png"
        
#         if not os.path.exists(image_path):
#             return {"error": f"Image file not found: {image_path}"}
        
#         img = PILImage.open(image_path)
#         mcp_img = to_mcp_image(img, format='png')
#         return mcp_img
        
#     except Exception as e:
#         import traceback
#         return {"error": f"Exception occurred while reading image: {str(e)}", "traceback": traceback.format_exc()}

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

# Create FastAPI app
app = FastAPI()

# Add middleware to validate the security token from query parameter
# @app.middleware("http")
# async def validate_api_key(request: Request, call_next):
#     # Authorization
#     auth_header = request.headers.get("Authorization")
#     API_KEY = os.getenv('MCP_KEY')
#     if auth_header != API_KEY:
#         logger.info(f"# Unauthorized request: {auth_header}")
#         raise HTTPException(status_code=401, detail="Invalid API key")
#     return await call_next(request)

@app.get("/test")
def test_endpoint():
    """
    Simple test endpoint to verify the server is running.
    Returns:
        dict: {"message": "Test endpoint is working!"}
    """
    logger.info("Calling test endpoint")
    return {"message": "Test endpoint is working!"}

app.mount("/", mcp.sse_app())

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting uvicorn server on {host}:{port}")
    
    uvicorn.run(
        "program:app",
        host=host,
        port=port,
        reload=False,  # Set to True for development
        log_level="info"
    )
