"""Prueba real y acotada de YOLO+ByteTrack, sin falsificar detecciones.

Ejemplo: python scripts/smoke_yolo_real.py --video pruebas/personas.mp4 --weights modelos/yolo11n.pt
No descarga pesos: exige archivo local. No modifica la base de datos.
"""
import argparse
import importlib.util
import json
from pathlib import Path


def preflight(video, weights):
    issues = []
    if not Path(video).is_file():
        issues.append(f"Video inexistente: {video}")
    if not Path(weights).is_file():
        issues.append(f"Pesos inexistentes (descárguelos antes): {weights}")
    if importlib.util.find_spec("ultralytics") is None:
        issues.append("Falta ultralytics: instale requirements.txt")
    if importlib.util.find_spec("cv2") is None:
        issues.append("Falta opencv-python")
    return issues


def run(video, weights, max_frames=30, tracker="bytetrack.yaml", details=False):
    if max_frames < 1:
        return {"status": "FAILED", "issues": ["max_frames debe ser positivo"], "frames": 0, "detections": 0}, 1
    issues = preflight(video, weights)
    if issues:
        return {"status": "BLOCKED", "issues": issues, "frames": 0, "detections": 0}, 2
    import cv2
    from ultralytics import YOLO
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        return {"status": "FAILED", "issues": ["OpenCV no pudo abrir el video"], "frames": 0, "detections": 0}, 1
    frames = detections = tracked = 0
    unique_track_ids = set()
    per_frame = []
    try:
        model = YOLO(str(weights))
        while frames < max_frames:
            ok, frame = cap.read()
            if not ok:
                break
            results = model.track(frame, persist=True, classes=[0], tracker=tracker, verbose=False)
            frames += 1
            frame_detections = frame_tracked = 0
            observations = []
            if results and results[0].boxes is not None:
                boxes = results[0].boxes
                frame_detections = len(boxes)
                detections += frame_detections
                if boxes.id is not None:
                    # Los IDs identifican trayectorias; no equivalen a clientes únicos.
                    ids = boxes.id.int().cpu().tolist()
                    frame_tracked = len(ids)
                    tracked += frame_tracked
                    unique_track_ids.update(int(track_id) for track_id in ids)
                if details:
                    coords = boxes.xyxy.cpu().tolist()
                    scores = boxes.conf.cpu().tolist()
                    ids_by_box = boxes.id.int().cpu().tolist() if boxes.id is not None else []
                    for i, (coords_i, score_i) in enumerate(zip(coords, scores)):
                        observations.append({"bbox_xyxy": [float(v) for v in coords_i],
                                             "confidence": float(score_i),
                                             "track_id": int(ids_by_box[i]) if i < len(ids_by_box) else None})
            entry = {"frame": frames, "detections": frame_detections, "tracked_boxes": frame_tracked}
            if details:
                # Las cajas sin ID también deben aparecer en la evidencia.
                if results and results[0].boxes is not None and results[0].boxes.id is None:
                    boxes = results[0].boxes
                    observations = [{"bbox_xyxy": [float(v) for v in coords], "confidence": float(score), "track_id": None}
                                    for coords, score in zip(boxes.xyxy.cpu().tolist(), boxes.conf.cpu().tolist())]
                entry["observations"] = observations
            per_frame.append(entry)
    except Exception as exc:
        # No perder los fotogramas ya procesados ni presentar la corrida como exitosa.
        return {"status": "FAILED", "issues": [f"{type(exc).__name__}: {exc}"],
                "frames": frames, "detections": detections, "tracked_boxes": tracked,
                "unique_track_ids": len(unique_track_ids), "per_frame": per_frame,
                "note": "Ejecución interrumpida: resultados parciales, no válidos como corrida completa."}, 1
    finally:
        cap.release()
    if not frames:
        return {"status": "FAILED", "issues": ["No se pudo leer ningún fotograma"], "frames": 0, "detections": 0}, 1
    return {"status": "EXECUTED", "frames": frames, "requested_frames": max_frames,
            "complete_requested_window": frames == max_frames,
            "detections": detections, "tracked_boxes": tracked,
            "unique_track_ids": len(unique_track_ids), "per_frame": per_frame,
            "note": "IDs de seguimiento no equivalen a clientes únicos; sin anotaciones no acredita precisión."}, 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--frames", type=int, default=30)
    parser.add_argument("--tracker", default="bytetrack.yaml")
    parser.add_argument("--output-json", help="Guardar evidencia JSON de la ejecución")
    parser.add_argument("--details", action="store_true", help="Incluir coordenadas, confianza e IDs por fotograma")
    args = parser.parse_args()
    if args.frames < 1:
        parser.error("--frames debe ser positivo")
    result, code = run(args.video, args.weights, args.frames, args.tracker, details=args.details)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.output_json:
        Path(args.output_json).write_text(output + "\n", encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
