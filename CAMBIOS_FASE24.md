# V26: integridad de evidencia ante interrupciones

- `scripts/smoke_yolo_real.py` conserva `per_frame`, conteos y IDs únicos si YOLO falla tras procesar algunos fotogramas. El estado permanece `FAILED` y el código de salida es 1.
- Las ejecuciones sin error informan `requested_frames` y `complete_requested_window`, evitando confundir un video corto con una muestra completa.
- Dos pruebas de regresión con modelos simulados; no equivalen a ejecutar YOLO real.
- Pendiente: instalación de Ultralytics, pesos `.pt`, validación real con `consumidor1.mp4` y anotaciones manuales.
