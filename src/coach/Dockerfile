FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the coach service source
COPY src/coach/ ./

# Copy shared database and model files if needed
COPY src/fit/database.py ./
COPY src/fit/models_db.py ./
COPY src/fit/models_dto.py ./

# Expose port
EXPOSE 5001

# Command to run the coach service
CMD ["python", "app.py"]