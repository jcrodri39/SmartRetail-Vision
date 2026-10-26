"""Evaluación de detección de personas por IoU contra anotaciones manuales.

Anotaciones: {"frames": [{"frame": 1, "boxes": [[x1,y1,x2,y2], ...]}]}.
Evidencia: JSON --details de scripts/smoke_yolo_real.py.
Solo evalúa los fotogramas anotados. No evalúa identidad/ByteTrack.
"""
import argparse
import json
from pathlib import Path


def iou(a, b):
    if len(a) != 4 or len(b) != 4:
        raise ValueError("Cada caja debe contener cuatro coordenadas")
    if any(not isinstance(x, (int, float)) or isinstance(x, bool) for x in [*a, *b]):
        raise ValueError("Coordenadas no numéricas")
    if a[2] <= a[0] or a[3] <= a[1] or b[2] <= b[0] or b[3] <= b[1]:
        raise ValueError("Caja inválida: x2>x1 e y2>y1 son obligatorios")
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2-x1)*max(0, y2-y1)
    area_a=(a[2]-a[0])*(a[3]-a[1])
    area_b=(b[2]-b[0])*(b[3]-b[1])
    return inter/(area_a+area_b-inter)


def evaluate(evidence, annotations, threshold=0.5):
    if not 0 < threshold <= 1:
        raise ValueError("El umbral IoU debe estar entre 0 (exclusivo) y 1")
    if evidence.get("status") != "EXECUTED":
        raise ValueError("Solo se admite evidencia de una ejecución YOLO real completada")
    predictions={}
    for item in evidence.get("per_frame", []):
        frame=item.get("frame")
        if not isinstance(frame,int) or frame < 1 or frame in predictions:
            raise ValueError("Fotograma duplicado o inválido en evidencia")
        if "observations" not in item:
            raise ValueError("Faltan observaciones: ejecutar YOLO con --details")
        predictions[frame]=[o["bbox_xyxy"] for o in item["observations"]]
    if not predictions:
        raise ValueError("No hay fotogramas en la evidencia")
    seen=set(); per_frame=[]; total_tp=total_fp=total_fn=0
    labeled=annotations.get("frames", [])
    if not labeled:
        raise ValueError("Se requiere al menos un fotograma anotado")
    for item in labeled:
        frame=item.get("frame")
        if not isinstance(frame,int) or frame in seen or frame not in predictions:
            raise ValueError(f"Fotograma anotado duplicado, inválido o no procesado: {frame}")
        seen.add(frame)
        gt=item["boxes"]
        pred=predictions[frame]
        # Verificar cajas, incluso si no hay emparejamientos.
        for box in [*gt,*pred]:
            iou(box,box)
        candidates=sorted(((iou(a,b),i,j) for i,a in enumerate(gt) for j,b in enumerate(pred)),reverse=True)
        used_gt=set();used_pred=set()
        for overlap,i,j in candidates:
            if overlap < threshold:
                break
            if i not in used_gt and j not in used_pred:
                used_gt.add(i);used_pred.add(j)
        tp=len(used_gt); fp=len(pred)-tp; fn=len(gt)-tp
        total_tp+=tp;total_fp+=fp;total_fn+=fn
        per_frame.append({"frame":frame,"tp":tp,"fp":fp,"fn":fn})
    precision=total_tp/(total_tp+total_fp) if total_tp+total_fp else 0.0
    recall=total_tp/(total_tp+total_fn) if total_tp+total_fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"status":"EVALUATED","iou_threshold":threshold,"annotated_frames":len(seen),
            "tp":total_tp,"fp":total_fp,"fn":total_fn,"precision":precision,
            "recall":recall,"f1":f1,"per_frame":sorted(per_frame,key=lambda x:x["frame"]),
            "scope":"Detección de personas solo en fotogramas anotados; no valida seguimiento ni permanencia."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence",required=True)
    parser.add_argument("--annotations",required=True)
    parser.add_argument("--iou",type=float,default=0.5)
    parser.add_argument("--output-json")
    args=parser.parse_args()
    try:
        result=evaluate(json.loads(Path(args.evidence).read_text(encoding="utf-8")),
                        json.loads(Path(args.annotations).read_text(encoding="utf-8")),args.iou)
    except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError) as exc:
        parser.exit(1,f"Error de evaluación: {exc}\n")
    output=json.dumps(result,indent=2,ensure_ascii=False)
    print(output)
    if args.output_json:
        Path(args.output_json).write_text(output+"\n",encoding="utf-8")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
