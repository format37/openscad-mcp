FROM python:3.11

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY solid_renderer.py /app/
COPY program.py /app/
COPY mcp_image_utils.py /app/
COPY server.py /app/

CMD ["python", "server.py"]
