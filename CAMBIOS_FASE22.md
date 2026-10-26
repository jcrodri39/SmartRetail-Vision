# Fase 22 — V24: evidencia de YOLO y ByteTrack

- `scripts/smoke_yolo_real.py` registra detecciones y cajas seguidas por fotograma, además del número de IDs de trayectoria distintos.
- Añadida opción `--output-json` para exportar evidencia verificable.
- Dos pruebas automatizadas con objetos simulados verifican conteos, IDs repetidos y fotogramas sin detecciones.
- **No se ha ejecutado YOLO real**: falta `ultralytics` y pesos `.pt` locales. Los tests de contrato no miden precisión.
- El video `consumidor1.mp4` debe pasarse mediante `--video`; no se incluye en el ZIP.

Ejemplo: `python scripts/smoke_yolo_real.py --video consumidor1.mp4 --weights yolo11n.pt --frames 654 --output-json evidencia_yolo.json`
