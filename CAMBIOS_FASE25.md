# Fase 25 — Evaluación reproducible de detecciones (V27)

Se añade `scripts/evaluate_yolo.py` para calcular TP/FP/FN, precisión, recall y F1 mediante emparejamiento uno a uno de cajas con IoU configurable. Solo acepta evidencia `EXECUTED` con `--details` y evalúa fotogramas anotados manualmente; no atribuye exactitud a datos simulados.

## Uso

1. Ejecutar YOLO real: `python scripts/smoke_yolo_real.py --video consumidor1.mp4 --weights yolo11n.pt --frames 654 --details --output-json evidencia.json`.
2. Editar `ejemplo_anotaciones.json` con cajas reales `[x1,y1,x2,y2]` de fotogramas elegidos, en coordenadas del video original.
3. Evaluar: `python scripts/evaluate_yolo.py --evidence evidencia.json --annotations ejemplo_anotaciones.json --iou 0.5 --output-json metricas.json`.

La plantilla contiene cajas vacías y NO constituye anotación real. El algoritmo no valida IDs de ByteTrack ni tiempo de permanencia.
