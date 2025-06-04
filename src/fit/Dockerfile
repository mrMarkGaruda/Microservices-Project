FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY ../../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy main.py from project root if needed for entrypoint
COPY ../../main.py .

ENV PYTHONPATH=/app
ENV FLASK_APP=app:app
ENV FLASK_ENV=production

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application using main.py as entrypoint
CMD ["python", "main.py"]