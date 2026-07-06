"""
Object-of-interest detector using YOLO11 (ultralytics).

Honest scope note: the pretrained yolo11n model is trained on COCO
(everyday objects -- person, car, truck, etc), not structural defects
like cracks or rust. This module runs real YOLO inference; any detected
object above the confidence threshold is logged for the demo pipeline.
A production version would fine-tune on a labeled defect dataset instead.

Note: loads a fresh YOLO model on every call rather than reusing one
cached instance -- avoids a known issue where calling the same loaded
model repeatedly across multiple images causes an internal fuse() error
on the second+ call. Slightly slower, but reliable for this demo's scale.
"""

import os
import cv2
from ultralytics import YOLO

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

CONFIDENCE_THRESHOLD = 0.3


def detect_anomalies(image_path: str) -> list:
    """
    Runs YOLO inference on one image.
    Returns a list of dicts: [{"label": str, "confidence": float, "bbox": [x1,y1,x2,y2]}, ...]
    """
    model = YOLO("yolo11n.pt")  # fresh instance each call, see module docstring
    results = model.predict(image_path, verbose=False)[0]

    detections = []
    for box in results.boxes:
        confidence = float(box.conf[0])
        if confidence < CONFIDENCE_THRESHOLD:
            continue
        label = model.names[int(box.cls[0])]
        bbox = box.xyxy[0].tolist()
        detections.append({
            "label": label,
            "confidence": round(confidence, 3),
            "bbox": [round(v, 2) for v in bbox],
        })

    annotated = results.plot()
    output_path = os.path.join(OUTPUT_DIR, os.path.basename(image_path))
    cv2.imwrite(output_path, annotated)

    return detections