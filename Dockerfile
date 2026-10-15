FROM python:3.9-slim

WORKDIR /app

# Install dependensi sistem dasar untuk OpenCV & GUI headless
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 app:app