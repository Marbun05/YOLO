# Deteksi Pintar

Install the dependencies and point the app at a local YOLOv8 model file:

```sh
pip install -r requirements.txt
python app.py
```

The app looks for `yolov8n.pt` beside `app.py`, in its parent directory, or at
`~/proyek_yolo/yolov8n.pt`, then lets Ultralytics resolve/download the standard
model name if none is found. Set `YOLO_MODEL_PATH` to override this search.
`CAMERA_INDEX` selects the preferred camera (default `0`); the app retries
camera opening and checks alternate indices/backends before reporting an error.

For production, serve one worker so the process owns a single webcam:

```sh
gunicorn --workers 1 --threads 8 --bind 127.0.0.1:5000 app:app
```

Open `http://127.0.0.1:5000/` for Beranda. The camera screen is at `/camera`;
the bottom tabs navigate to `/`, `/history`, and `/settings`. The backend
annotates its MJPEG stream at `/video_feed` and provides current per-class
counts as JSON at `/api/counts`. The camera page starts and stops a session at
`/api/save_log`; stopping submits its timestamp and per-class counts, which are
appended to `logs.json` beside `app.py`. `/api/logs` returns saved sessions for
the history page, where a card can be expanded for its timestamp, object counts,
and notes; `DELETE /api/logs/<log_id>` removes a saved session.

The settings page reads and updates the live detector configuration through
`GET /api/settings` and `POST /api/settings`. The JSON body contains `classes`
(an array of COCO class IDs from 0 to 79) and `confidence` (a number from 0 to 1),
for example `{"classes":[0,2,3,7],"confidence":0.5}`. Changes are applied to
subsequent camera-frame predictions.
# YOLO
