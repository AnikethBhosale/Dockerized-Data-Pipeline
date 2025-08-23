FROM python:3.10-slim

# Set working directory
WORKDIR /opt/dagster/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY workspace.yaml .
COPY stock_pipeline/ ./stock_pipeline/

# Create Dagster home directory
RUN mkdir -p /opt/dagster/dagster_home

# Expose port
EXPOSE 3000

# Set environment variables
ENV DAGSTER_HOME=/opt/dagster/dagster_home
ENV PYTHONPATH=/opt/dagster/app

# Default command
CMD ["dagster-webserver", "-h", "0.0.0.0", "-p", "3000", "-w", "/opt/dagster/app/workspace.yaml"]
