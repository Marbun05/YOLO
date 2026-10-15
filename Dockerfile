FROM python:3.9-slim

WORKDIR /app

# Set environment agar Ultralytics tidak menulis ke /root/.config yang read-only
ENV YOLOV8_CONFIG_DIR=/tmp/ultralytics
ENV ULTRALYTICS_CONFIG_DIR=/tmp/ultralytics

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Download model YOLOv8n ke direktori lokal /app saat build
RUN curl -L https://github.com/ultralytics/assets/releases/download/v8.4.0/yolov8n.pt -o /app/yolov8n.pt

EXPOSE 8080

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 8 app:app"]
