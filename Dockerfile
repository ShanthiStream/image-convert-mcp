FROM python:3.11-slim

WORKDIR /app

# Install dependencies with minimal packages to reduce memory usage
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    libpng-dev \
    libavif-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY mcp_server.py .

# Use exec to ensure proper signal handling while allowing environment variable expansion
CMD exec python mcp_server.py --transport sse --host 0.0.0.0 --port ${PORT:-8000}
