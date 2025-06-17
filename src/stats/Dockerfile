FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5002
ENV STATS_DATABASE_URL="postgresql://stats_user:stats_password@stats_db:5432/stats_db"
ENV STATS_SERVICE_PORT=5002
CMD ["python", "app.py"]