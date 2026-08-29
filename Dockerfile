# Use official lightweight Python image
FROM python:3.11-slim

# Prevent Python from writing pyc files & enable logs immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed by lxml, bs4, etc.
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    libfreetype6-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better Docker cache usage)
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy code
COPY backend backend
COPY frontend frontend
COPY start.sh .

# Make script executable
RUN chmod +x start.sh

# Streamlit default port
ENV PORT=8501

EXPOSE 8501

CMD ["bash", "start.sh"]
