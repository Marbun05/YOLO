import cv2
from datetime import datetime
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
# ID Kelas COCO: 0=person, 2=car, 3=motorcycle, 7=truck
target_classes = [0, 2, 3, 7]
class_names = {0: "Orang", 2: "Mobil", 3: "Motor", 7: "Truk"}

# Buka stream webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Jalankan prediksi pada frame aktif
    results = model.predict(frame, classes=target_classes, verbose=False)
    boxes = results[0].boxes

    # Hitung jumlah objek per kategori
    counts = {name: 0 for name in class_names.values()}
    total_count = 0

    if boxes is not None:
        for box in boxes:
            cls_id = int(box.cls[0].item())
            if cls_id in class_names:
                counts[class_names[cls_id]] += 1
                total_count += 1

    # Gambarkan kotak hasil deteksi
    annotated_frame = results[0].plot()

    # Tampilkan jumlah total objek di layar webcam
    cv2.putText(
        annotated_frame,
        f"Total Objek: {total_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )

    cv2.imshow("Deteksi & Counter YOLO", annotated_frame)

    key = cv2.waitKey(1) & 0xFF
    # Tekan 's' untuk menyimpan log teks ke file
    if key == ord("s"):
        waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rincian_objek = ", ".join(
            [f"{nama}: {jumlah}" for nama, jumlah in counts.items()]
        )
        baris_log = f"[{waktu_sekarang}] Total: {total_count} | Rincian: {rincian_objek}\n"

        with open("log_deteksi.txt", "a") as f:
            f.write(baris_log)
        print(f"Log tersimpan: {baris_log.strip()}")

    # Tekan 'q' untuk keluar
    elif key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()