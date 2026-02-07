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
COPY src/ ./src/

# Copy and set up entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Use JSON array form for proper signal handling
ENTRYPOINT ["./entrypoint.sh"]
