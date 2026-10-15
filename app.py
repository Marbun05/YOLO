import os
import json
import logging
import base64
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from ultralytics import YOLO
from supabase import create_client, Client

app = Flask(__name__)

# Muat model YOLO dari file lokal dengan aman
model_path = os.path.join(os.path.dirname(__file__), "yolov8n.pt")
model = YOLO(model_path)

# Ambil URL dan API Key dari Environment Variables
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Buat koneksi client ke Supabase jika URL dan KEY tersedia
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None

BASE_DIR = Path(__file__).resolve().parent
UI_DIR = BASE_DIR
LOG_FILE_PATH = BASE_DIR / "logs.json"
LOG_LOCK = threading.Lock()
LOGGER = logging.getLogger(__name__)

app_config = {"classes": [0, 2, 3, 5, 7], "confidence": 0.50}
APP_CONFIG_LOCK = threading.Lock()


@app.get("/")
@app.get("/home")
def home():
    return send_from_directory(UI_DIR, "index.html")


@app.get("/camera")
def camera():
    return send_from_directory(UI_DIR / "kamera_deteksi_pintar", "kamera.html")


@app.get("/settings")
def settings():
    return send_from_directory(UI_DIR / "pengaturan_deteksi_pintar", "pengaturan.html")


@app.get("/history")
def history():
    return send_from_directory(UI_DIR / "riwayat_deteksi_deteksi_pintar", "riwayat.html")


@app.get("/api/settings")
def get_settings():
    with APP_CONFIG_LOCK:
        config = {
            "classes": app_config["classes"].copy(),
            "confidence": app_config["confidence"],
        }
    return jsonify(config)


@app.post("/api/settings")
def update_settings():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    classes = payload.get("classes")
    confidence = payload.get("confidence")
    if (
        not isinstance(classes, list)
        or any(
            isinstance(class_id, bool)
            or not isinstance(class_id, int)
            or not 0 <= class_id <= 79
            for class_id in classes
        )
    ):
        return jsonify({"error": "Classes must be a list of integer IDs from 0 to 79."}), 400
    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= confidence <= 1
    ):
        return jsonify({"error": "Confidence must be a number between 0 and 1."}), 400

    with APP_CONFIG_LOCK:
        app_config["classes"] = sorted(set(classes))
        app_config["confidence"] = float(confidence)
        config = {
            "classes": app_config["classes"].copy(),
            "confidence": app_config["confidence"],
        }
    return jsonify(config)


@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json() or {}
        image_data = data.get('image', '')

        if not image_data:
            return jsonify({'error': 'Tidak ada gambar'}), 400

        header, encoded = image_data.split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        with APP_CONFIG_LOCK:
            classes = app_config["classes"]
            conf = app_config["confidence"]

        results = model(img, classes=classes, conf=conf, verbose=False)[0]

        detections = []
        counts_dict = {}

        for box in results.boxes:
            cls_id = int(box.cls[0])
            name = model.names[cls_id]
            confidence_val = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()

            counts_dict[name] = counts_dict.get(name, 0) + 1

            detections.append({
                'class': name,
                'confidence': round(confidence_val, 2),
                'box': [int(v) for v in xyxy]
            })

        return jsonify({
            'status': 'success',
            'counts': counts_dict,
            'detections': detections,
            'image_width': img.shape[1],
            'image_height': img.shape[0]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- LOG LOKAL (logs.json) & SUPABASE ---
def read_logs_from_file():
    if not LOG_FILE_PATH.exists():
        return []
    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def write_logs_to_file(logs):
    tmp_path = LOG_FILE_PATH.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, LOG_FILE_PATH)


@app.get("/api/logs")
def get_logs():
    try:
        with LOG_LOCK:
            logs_data = read_logs_from_file()

        if supabase:
            try:
                res = supabase.table("logs").select("*").order("created_at", desc=True).execute()
                if res.data:
                    supa_list = []
                    for item in res.data:
                        created = item.get("created_at") or datetime.now(timezone.utc).isoformat()
                        supa_list.append({
                            "id": str(item.get("id", uuid4())),
                            "created_at": created,
                            "ended_at": created,
                            "counts": item.get("counts", {}),
                            "notes": item.get("notes", ""),
                            "location": item.get("location", ""),
                            "duration": item.get("duration", "00:00"),
                        })
                    supa_list.reverse()
                    return jsonify(supa_list)
            except Exception as se:
                LOGGER.warning("Supabase read error: %s", se)

        return jsonify(logs_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/save_log', methods=['POST'])
def save_api_log():
    try:
        data = request.get_json() or {}
        if data.get('action') != 'stop':
            return jsonify({"status": "ok"})

        counts_payload = data.get('counts', {})
        notes = data.get('notes', '')
        location = data.get('location', 'Lokasi tidak diisi')
        duration = data.get('duration', '00:00')
        timestamp = datetime.now(timezone.utc).isoformat()

        new_entry = {
            "id": str(uuid4()),
            "created_at": timestamp,
            "ended_at": timestamp,
            "counts": counts_payload,
            "notes": notes,
            "location": location,
            "duration": duration,
            "total": sum(counts_payload.values()) if isinstance(counts_payload, dict) else 0,
        }

        with LOG_LOCK:
            logs = read_logs_from_file()
            logs.append(new_entry)
            write_logs_to_file(logs)

        if supabase:
            try:
                supabase.table("logs").insert({
                    "counts": counts_payload,
                    "notes": notes,
                    "location": location,
                    "duration": duration,
                }).execute()
            except Exception as se:
                LOGGER.warning("Supabase insert error: %s", se)

        return jsonify({"status": "success", "message": "Log berhasil disimpan!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.delete("/api/logs/<log_id>")
def delete_log(log_id):
    try:
        deleted_local = False
        deleted_remote = False

        with LOG_LOCK:
            logs = read_logs_from_file()
            remaining = [l for l in logs if str(l.get("id")) != str(log_id)]
            if len(remaining) != len(logs):
                write_logs_to_file(remaining)
                deleted_local = True

        if supabase:
            try:
                res = supabase.table("logs").delete().eq("id", log_id).execute()
                deleted_remote = bool(res.data)
            except Exception as se:
                LOGGER.warning("Supabase delete error: %s", se)

        if deleted_local or deleted_remote:
            return jsonify({"status": "deleted", "id": log_id})
        return jsonify({"error": "Log tidak ditemukan."}), 404
    except Exception as e:
        LOGGER.exception("Could not delete detection log %s", log_id)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=False,
        threaded=True,
    )
