FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH \
    HOST=0.0.0.0 PORT=7860 YOLO_CONFIG_DIR=/tmp/Ultralytics
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user . .
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

EXPOSE 7860
CMD ["python", "app.py"]