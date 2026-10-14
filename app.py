import base64
import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import NAMESPACE_URL, uuid4, uuid5

import cv2
import numpy as np
from flask import Flask, request, jsonify, send_from_directory, Response
from ultralytics import YOLO
from supabase import create_client, Client

app = Flask(__name__)
model = YOLO('yolov8n.pt')

# Ambil URL dan API Key dari Environment Variables
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Buat koneksi client ke Supabase jika URL dan KEY tersedia
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None

BASE_DIR = Path(__file__).resolve().parent
UI_DIR = BASE_DIR
CONFIGURED_MODEL_PATH = os.environ.get("YOLO_MODEL_PATH")
MODEL_CANDIDATES = (
    BASE_DIR / "yolov8n.pt",
    BASE_DIR.parent / "yolov8n.pt",
    Path.home() / "proyek_yolo" / "yolov8n.pt",
)
CAMERA_INDEX = int(os.environ.get("CAMERA_INDEX", "0"))
CAMERA_RETRIES = 3
CAMERA_RETRY_DELAY = 0.5
CLASS_NAMES = {0: "person", 2: "car", 3: "motorcycle", 7: "truck"}
INITIAL_COUNTS = {name: 0 for name in CLASS_NAMES.values()}
app_config = {"classes": [0, 2, 3, 5, 7], "confidence": 0.50}
APP_CONFIG_LOCK = threading.Lock()
LOGGER = logging.getLogger(__name__)
LOG_PATH = BASE_DIR / "logs.json"
LOG_LOCK = threading.Lock()
LOG_FILE_PATH = BASE_DIR / "logs.json"

def load_model():
    if CONFIGURED_MODEL_PATH:
        model_path = Path(CONFIGURED_MODEL_PATH).expanduser()
        if not model_path.is_file():
            raise FileNotFoundError(f"YOLO model file not found: {model_path}")
        return YOLO(str(model_path))

    for candidate in MODEL_CANDIDATES:
        if candidate.is_file():
            LOGGER.info("Loading YOLO model from %s", candidate)
            return YOLO(str(candidate))

    LOGGER.info("No local yolov8n.pt found; asking Ultralytics to resolve the model")
    return YOLO("yolov8n.pt")


def open_camera():
    camera_indices = list(dict.fromkeys([CAMERA_INDEX, 0, 1, 2, 3]))
    backends = [cv2.CAP_ANY]
    if hasattr(cv2, "CAP_V4L2"):
        backends.insert(0, cv2.CAP_V4L2)

    for attempt in range(CAMERA_RETRIES):
        for camera_index in camera_indices:
            for backend in backends:
                capture = cv2.VideoCapture(camera_index, backend)
                if capture.isOpened():
                    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    ok, frame = capture.read()
                    if ok and frame is not None:
                        LOGGER.info(
                            "Opened webcam at index %s using backend %s",
                            camera_index,
                            backend,
                        )
                        return capture, frame
                capture.release()

        if attempt < CAMERA_RETRIES - 1:
            LOGGER.warning(
                "Could not open a readable webcam; retrying (%s/%s)",
                attempt + 1,
                CAMERA_RETRIES - 1,
            )
            time.sleep(CAMERA_RETRY_DELAY)

    raise RuntimeError(
        f"Could not open a readable webcam. Tried indices {camera_indices}; "
        "check camera permissions or set CAMERA_INDEX."
    )


class CameraDetector:
    def __init__(self):
        self.condition = threading.Condition()
        self.stream_lock = threading.Lock()
        self.status = "idle"
        self.error = None
        self.counts = INITIAL_COUNTS.copy()
        self.updated_at = None
        self.recording_started_at = None

    def snapshot(self):
        with self.condition:
            return {
                "status": self.status,
                "error": self.error,
                "counts": self.counts.copy(),
                "total": sum(self.counts.values()),
                "updated_at": self.updated_at,
            }

    def stream(self):
        with self.stream_lock:
            capture = None
            failed = False
            try:
                model_inst = load_model()
                capture, frame = open_camera()
                with APP_CONFIG_LOCK:
                    config = {
                        "classes": app_config["classes"].copy(),
                        "confidence": app_config["confidence"],
                    }
                results = model_inst.predict(
                    frame,
                    classes=config["classes"],
                    conf=config["confidence"],
                    imgsz=640,
                    verbose=False,
                )
                with self.condition:
                    self.status = "running"
                    self.error = None
                    self.condition.notify_all()

                while True:
                    counts = INITIAL_COUNTS.copy()
                    boxes = results[0].boxes
                    if boxes is not None:
                        for class_id in boxes.cls.int().tolist():
                            name = CLASS_NAMES.get(class_id)
                            if name:
                                counts[name] += 1

                    annotated_frame = results[0].plot()
                    encoded, buffer = cv2.imencode(
                        ".jpg", annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80]
                    )
                    if not encoded:
                        raise RuntimeError("Could not encode the annotated camera frame.")

                    with self.condition:
                        self.counts = counts
                        self.updated_at = datetime.now(timezone.utc).isoformat()
                        self.condition.notify_all()

                    yield (
                        b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                        + buffer.tobytes()
                        + b"\r\n"
                    )

                    ok, frame = capture.read()
                    if not ok or frame is None:
                        LOGGER.warning("Webcam frame read failed; reopening the camera")
                        capture.release()
                        capture, frame = open_camera()
                    with APP_CONFIG_LOCK:
                        config = {
                            "classes": app_config["classes"].copy(),
                            "confidence": app_config["confidence"],
                        }
                    results = model_inst.predict(
                        frame,
                        classes=config["classes"],
                        conf=config["confidence"],
                        imgsz=640,
                        verbose=False,
                    )
            except GeneratorExit:
                raise
            except Exception as exc:
                failed = True
                LOGGER.exception("Camera detection stopped")
                with self.condition:
                    self.status = "error"
                    self.error = str(exc)
                    self.condition.notify_all()
            finally:
                if capture is not None:
                    capture.release()
                if not failed:
                    with self.condition:
                        self.status = "idle"
                        self.condition.notify_all()


detector = CameraDetector()


def serve_page(directory):
    return send_from_directory(UI_DIR / directory, "code.html")


@app.get("/")
def home():
    return serve_page("beranda_deteksi_pintar")


@app.get("/camera")
def camera():
    return serve_page("kamera_deteksi_pintar")


@app.get("/home")
def home_alias():
    return serve_page("beranda_deteksi_pintar")


@app.get("/settings")
def settings():
    return serve_page("pengaturan_deteksi_pintar")


@app.get("/history")
def history():
    return serve_page("riwayat_deteksi_deteksi_pintar")


@app.get("/api/counts")
def counts():
    data = detector.snapshot()
    return jsonify(data), 503 if data["status"] == "error" else 200


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

        # Jalankan YOLO tanpa filter ketat agar ponsel & semua objek tertangkap
        results = model(img, conf=0.30, verbose=False)[0]

        detections = []
        counts_dict = {}

        for box in results.boxes:
            cls_id = int(box.cls[0])
            name = model.names[cls_id]
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()

            # Hitung semua objek yang terdeteksi
            counts_dict[name] = counts_dict.get(name, 0) + 1

            detections.append({
                'class': name,
                'confidence': round(conf, 2),
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


# --- FILE PATH LOGS LOKAL PASTI ---
LOG_FILE_PATH = BASE_DIR / "logs.json"

def get_all_logs_safe():
    if not LOG_FILE_PATH.exists():
        return []
    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

@app.get("/api/logs")
def get_logs():
    logs_data = get_all_logs_safe()
    
    # Jika Supabase aktif dan memiliki data, gunakan Supabase
    if supabase:
        try:
            res = supabase.table("logs").select("*").order("created_at", desc=True).execute()
            if res.data and len(res.data) > 0:
                supa_list = []
                for item in res.data:
                    supa_list.append({
                        "id": str(item.get("id", uuid4())),
                        "ended_at": item.get("created_at", datetime.now(timezone.utc).isoformat()),
                        "created_at": item.get("created_at", datetime.now(timezone.utc).isoformat()),
                        "counts": item.get("counts", {}),
                        "notes": item.get("notes", ""),
                        "location": item.get("location", ""),
                        "duration": item.get("duration", "00:00")
                    })
                return jsonify(supa_list)
        except Exception as e:
            LOGGER.warning("Gagal baca Supabase: %s", e)

    # Selalu return array lokal jika Supabase kosong/error
    return jsonify(logs_data)


@app.post("/api/save_log")
def save_log():
    try:
        data = request.get_json() or {}
        if data.get("action") == "stop":
            counts_payload = data.get("counts", {})
            notes = data.get("notes", "")
            location = data.get("location", "")
            duration = data.get("duration", "00:00")
            now_iso = datetime.now(timezone.utc).isoformat()

            new_entry = {
                "id": str(uuid4()),
                "ended_at": now_iso,
                "created_at": now_iso,
                "counts": counts_payload,
                "notes": notes,
                "location": location,
                "duration": duration,
                "total": sum(counts_payload.values()) if isinstance(counts_payload, dict) else 0
            }

            # 1. PAKSA TULIS LANGSUNG KE FILE LOKAL LOGS.JSON
            existing_logs = get_all_logs_safe()
            existing_logs.append(new_entry)
            
            with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(existing_logs, f, ensure_ascii=False, indent=2)

            # 2. KIRIM KE SUPABASE JIKA ADA
            if supabase:
                try:
                    supabase.table("logs").insert({
                        "counts": counts_payload,
                        "notes": notes,
                        "location": location,
                        "duration": duration
                    }).execute()
                except Exception as se:
                    LOGGER.warning("Gagal kirim Supabase: %s", se)

            return jsonify({"status": "success", "message": "Log tersimpan!"})

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def read_logs_from_file():
    if not LOG_FILE_PATH.exists():
        return []
    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        # 1. Selalu baca dari file lokal logs.json terlebih dahulu
        logs_data = read_logs_from_file()

        # 2. Jika Supabase aktif dan berisi data, gabungkan / utamakan Supabase
        if supabase:
            try:
                res = supabase.table("logs").select("*").order("created_at", desc=True).execute()
                if res.data and len(res.data) > 0:
                    supa_list = []
                    for item in res.data:
                        supa_list.append({
                            "id": str(item.get("id", uuid4())),
                            "created_at": item.get("created_at", datetime.now(timezone.utc).isoformat()),
                            "ended_at": item.get("created_at", datetime.now(timezone.utc).isoformat()),
                            "counts": item.get("counts", {}),
                            "notes": item.get("notes", ""),
                            "location": item.get("location", ""),
                            "duration": item.get("duration", "00:00")
                        })
                    return jsonify(supa_list)
            except Exception as se:
                LOGGER.warning("Supabase read error: %s", se)

        # Kembalikan daftar log lokal
        return jsonify(logs_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/save_log', methods=['POST'])
def save_log():
    try:
        data = request.get_json() or {}
        action = data.get('action')

        if action == 'stop':
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
                "total": sum(counts_payload.values()) if isinstance(counts_payload, dict) else 0
            }

            # SELALU SIMPAN KE LOGS.JSON LOKAL
            logs = read_logs_from_file()
            logs.append(new_entry)
            with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)

            # COBA SIMPAN KE SUPABASE (TANPA MELEMPARKAN EXCEPTION JIKA GAGAL)
            if supabase:
                try:
                    supabase.table("logs").insert({
                        "counts": counts_payload,
                        "notes": notes,
                        "location": location,
                        "duration": duration
                    }).execute()
                except Exception as se:
                    LOGGER.warning("Supabase insert error: %s", se)

            return jsonify({"status": "success", "message": "Log berhasil disimpan!"})

        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.delete("/api/logs/<log_id>")
def delete_log(log_id):
    try:
        if supabase:
            supabase.table("logs").delete().eq("id", log_id).execute()
            return jsonify({"status": "deleted", "id": log_id})
        return jsonify({"error": "Supabase tidak terkonfigurasi."}), 400
    except Exception as e:
        LOGGER.exception("Could not delete detection log %s", log_id)
        return jsonify({"error": str(e)}), 500


@app.get("/video_feed")
def video_feed():
    return Response(
        detector.stream(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=False,
        threaded=True,
    )