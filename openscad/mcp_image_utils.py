import base64
import io
import requests

from PIL import Image as PILImage
from mcp.server.fastmcp import Image as MCPImage


def pil_to_base64(image: PILImage.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str


def base64_to_pil(data_base64: str) -> PILImage.Image:
    image = PILImage.open(io.BytesIO(base64.b64decode(data_base64)))
    return image


def retrieve_image_from_url(image_url: str) -> PILImage.Image:
    """
    Retrieve an image from a given URL and return it as a PIL Image object.
    """
    response = requests.get(image_url)
    response.raise_for_status()
    image_data = io.BytesIO(response.content)
    return PILImage.open(image_data)


def load_image(image: str | bytes | io.BufferedReader) -> PILImage.Image:
    """
    Load an image from a file path, URL, or raw bytes.

    Args:
        image: Image file path, URL, or raw bytes.

    Returns:
        PIL Image object.
    """
    if isinstance(image, io.BufferedReader):
        image = image.read()
        return PILImage.open(io.BytesIO(image))
    elif isinstance(image, bytes):
        return PILImage.open(io.BytesIO(image))
    elif os.path.isfile(image):
        return PILImage.open(image)
    elif image.startswith("http://") or image.startswith("https://"):
        return retrieve_image_from_url(image)
    else:
        raise ValueError(f"Invalid image path or URL: {image}")


def to_mcp_image(image: PILImage.Image | bytes, format: str = "jpeg") -> MCPImage:
    """
    Convert a PIL Image object or bytes to an MCP Image.

    Args:
        image: PIL Image object or bytes containing image data
        format: Format to save the image in (default is "jpeg")

    Returns:
        MCP Image object with specified format
    """
    if isinstance(image, io.BufferedReader):
        image_bytes = image.read()
    elif isinstance(image, bytes):
        image_bytes = image
    elif isinstance(image, PILImage.Image):
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        image_bytes = img_byte_arr.getvalue()
    else:
        raise ValueError("Invalid image type. Expected PIL Image or bytes.")

    return MCPImage(data=image_bytes, format=format)