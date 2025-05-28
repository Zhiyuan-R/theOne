# theOne Dating App - Production Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories for persistent data
RUN mkdir -p /app/data/database \
    && mkdir -p /app/data/uploads/profiles \
    && mkdir -p /app/data/uploads/expectations \
    && mkdir -p /app/data/uploads/ideal_partners \
    && mkdir -p /app/data/backups \
    && mkdir -p logs

# Create symbolic links to persistent storage (will be overridden by volume mounts)
RUN mkdir -p static/uploads \
    && ln -sf /app/data/uploads/profiles static/uploads/profiles \
    && ln -sf /app/data/uploads/expectations static/uploads/expectations \
    && ln -sf /app/data/uploads/ideal_partners static/uploads/ideal_partners

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app \
    && chown -R appuser:appuser /app/data
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
