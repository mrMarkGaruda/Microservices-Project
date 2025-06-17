# Use a slim Python image for a production-ready build
FROM python:3.12-slim

WORKDIR /app

# Prevent Python from writing pyc files to disk and ensure stdout/stderr is unbuffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

# Install dependencies
COPY pyproject.toml uv.lock ./
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY main_coach.py /app/main_coach.py
COPY src /app/src

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "main_coach.py"]