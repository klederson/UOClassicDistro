# Dockerfile for POL Server
FROM ubuntu:22.04

# Install necessary packages
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libssl-dev \
    libmysqlclient-dev \
    zlib1g-dev \
    python3 \
    python3-pip \
    supervisor \
    wget \
    curl \
    screen \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for API
RUN pip3 install \
    fastapi \
    uvicorn \
    pydantic \
    python-multipart \
    aiofiles \
    psutil \
    watchdog

# Create POL user
RUN useradd -m -s /bin/bash pol

# Set working directory
WORKDIR /workspace

# Copy POL server files
COPY . /workspace/
RUN chown -R pol:pol /workspace

# Create directories for logs and data
RUN mkdir -p /workspace/logs /workspace/data /workspace/accounts

# Expose ports
EXPOSE 5003 8000

# Switch to pol user
USER pol

# Start command will be handled by docker-compose
CMD ["/usr/bin/supervisord", "-c", "/workspace/supervisord.conf"]