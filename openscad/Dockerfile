FROM python:3.11

# Install OpenSCAD and headless rendering dependencies
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       openscad \
       xvfb \
       xauth \
       libgl1 \
       libglu1-mesa \
       libgl1-mesa-dri \
       ca-certificates \
       fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Create a lightweight wrapper so any 'openscad' call runs under Xvfb
RUN printf '#!/bin/sh\nexec xvfb-run -a --server-args="-screen 0 1600x1200x24 -nolisten tcp" /usr/bin/openscad "$@"\n' > /usr/local/bin/openscad \
    && chmod +x /usr/local/bin/openscad

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY mcp_image_utils.py /app/
COPY server.py /app/

ENV PORT=8004
EXPOSE 8004

CMD ["python", "server.py"]
