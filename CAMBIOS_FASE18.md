# Fase 18 — Prueba real reproducible de YOLO y ByteTrack

Se agregó `scripts/smoke_yolo_real.py`, que **no utiliza mocks**. Exige un video y pesos locales, verifica dependencias, ejecuta `YOLO.track(..., persist=True, tracker="bytetrack.yaml")` y devuelve JSON con fotogramas, detecciones y cajas con ID de seguimiento. Si faltan recursos, devuelve `BLOCKED` y código 2, en lugar de fingir éxito. `EXECUTED` significa que corrió el modelo, no que la precisión esté validada.

Ejecutar: `python scripts/smoke_yolo_real.py --video ruta/video.mp4 --weights ruta/yolo11n.pt --frames 30`

No se incluyen videos de personas ni pesos del modelo en el proyecto. No se ha validado aún precisión, ni integración real del modelo con SQLite y dashboard. Las pruebas añadidas comprueban la ruta de bloqueo cuando faltan recursos.
