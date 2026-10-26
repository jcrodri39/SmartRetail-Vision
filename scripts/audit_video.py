"""Auditoría reproducible de legibilidad y cambios visuales; NO detecta personas."""
import argparse
import json
from pathlib import Path


def audit_video(path, sample_stride=30):
    import cv2
    if sample_stride < 1:
        raise ValueError("sample_stride debe ser >= 1")
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError("No se puede abrir el video")
    fps = cap.get(cv2.CAP_PROP_FPS)
    expected = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    decoded = 0
    sampled = 0
    change_sum = 0.0
    prev = None
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if decoded % sample_stride == 0:
                gray = cv2.cvtColor(cv2.resize(frame, (160, 90)), cv2.COLOR_BGR2GRAY)
                if prev is not None:
                    change_sum += float(cv2.absdiff(gray, prev).mean())
                prev = gray
                sampled += 1
            decoded += 1
    finally:
        cap.release()
    return {"video": Path(path).name, "width": width, "height": height,
            "fps": round(fps, 4), "frames_reported": expected,
            "frames_decoded": decoded, "all_reported_frames_decoded": expected == decoded if expected > 0 else None,
            "duration_seconds_estimated": round(decoded / fps, 3) if fps > 0 else None,
            "samples": sampled, "mean_sample_frame_change_0_255": round(change_sum / (sampled - 1), 4) if sampled > 1 else None,
            "scope": "Diagnóstico de decodificación y variación de imagen; no mide detección, identidad ni precisión de YOLO."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video")
    parser.add_argument("--stride", type=int, default=30)
    args = parser.parse_args()
    print(json.dumps(audit_video(args.video, args.stride), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
