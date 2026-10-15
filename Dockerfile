FROM python:3.9-slim

WORKDIR /app

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

RUN curl -L https://github.com/ultralytics/assets/releases/download/v8.4.0/yolov8n.pt -o /app/yolov8n.pt

# Hapus EXPOSE statis atau biarkan, lalu gunakan port dinamis $PORT dari Railway
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 app:app
