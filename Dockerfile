FROM python:3.12

# Install system dependencies including wkhtmltopdf
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    wkhtmltopdf \
    xfonts-base \
    fontconfig \
    libjpeg62-turbo \
    libxrender1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Set working directory
WORKDIR /app

# Upgrade pip and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project code
COPY . .

# Expose the port your app runs on
EXPOSE 8000

# Start the Django app with Gunicorn
CMD ["gunicorn", "Tara.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=2"]
