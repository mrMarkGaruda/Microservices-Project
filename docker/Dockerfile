FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire src directory
COPY src/ ./src/

# Set Python path to include src directory
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 5000

# Command to run the monolith service
CMD ["python", "-m", "src.fit.app"]