FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5003

ENV BILLING_DATABASE_URL="postgresql://billing_user:billing_password@billing_db:5432/billing_db"
ENV BILLING_SERVICE_PORT=5003
ENV LOG_LEVEL=INFO

CMD ["python", "app.py"]
