# ---------- STAGE 1: Builder ----------
FROM python:3.12-slim AS builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PIP_CACHE_DIR=/root/.cache/pip

# Copy only requirements for caching
COPY requirements.txt .

# Install Python dependencies using BuildKit cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --cache-dir=/root/.cache/pip -r requirements.txt

# ---------- STAGE 2: Runtime ----------
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:/usr/local/bin:$PATH" \
    PYTHONPATH=/app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libpq5 \
    fontconfig \
    xfonts-75dpi \
    xfonts-base \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf
RUN curl -fSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb -o /tmp/wkhtmltopdf.deb \
    && apt-get install -y --no-install-recommends /tmp/wkhtmltopdf.deb \
    && rm -f /tmp/wkhtmltopdf.deb \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && wkhtmltopdf --version

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv

# Copy project files
COPY . .

# Example CMD for Django (adjust if needed)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
