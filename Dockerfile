# ---------- STAGE 1: Builder ----------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies including wkhtmltopdf
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    xfonts-base \
    fontconfig \
    libjpeg62-turbo \
    libxrender1 \
    wkhtmltopdf \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---------- STAGE 2: Runtime ----------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install runtime dependencies including wkhtmltopdf
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    xfonts-base \
    fontconfig \
    libjpeg62-turbo \
    libxrender1 \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*


# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Expose the port your app runs on
EXPOSE 8000


CMD ["gunicorn", "Tara.wsgi:application", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "2"]

