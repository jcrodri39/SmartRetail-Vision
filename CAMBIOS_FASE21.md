# Fase 21 — V23: exclusión de procesos concurrentes

- `LiveVision.start` devuelve `False` cuando hay un worker vivo o ejecución activa; evita sobreescritura de `camera_id`, métricas y datos de seguimiento.
- `stop` solicita la parada pero no presupone que el hilo ya finalizó.
- Endpoint `POST /vision/start/{cid}` responde HTTP 409 si hay una ejecución en curso.
- Dos pruebas unitarias: inicio concurrente y fallo al crear el hilo.
- No se ha probado YOLO real: Ultralytics y pesos no disponibles.
