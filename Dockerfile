FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Download model yolov8n.pt saat build image agar siap pakai
RUN curl -L https://github.com/ultralytics/assets/releases/download/v8.4.0/yolov8n.pt -o yolov8n.pt

EXPOSE 8080

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 app:app"]
