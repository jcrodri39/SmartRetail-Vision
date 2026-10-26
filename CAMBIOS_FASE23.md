# V25 — Evidencia detallada de YOLO/ByteTrack

- `scripts/smoke_yolo_real.py` acepta `--details` y añade `observations` por fotograma con caja `bbox_xyxy`, confianza y `track_id` (o `null` si no hay seguimiento).
- Sin `--details`, se conserva el formato resumido previo.
- Rechaza `max_frames` no positivo también cuando se invoca desde Python.
- Añadidas pruebas automatizadas para la evidencia y la validación de parámetros.

## Ejecución pendiente con modelo real

```bash
python scripts/smoke_yolo_real.py --video consumidor1.mp4 --weights yolo11n.pt --frames 654 --details --output-json evidencia_yolo.json
```

**No se ha validado YOLO real**: el entorno de construcción no incluye Ultralytics ni pesos `.pt`. Los tests de evidencia emplean dobles simulados del modelo.
