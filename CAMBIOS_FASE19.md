# Fase 19: comprobación con video aportado

Archivo: consumidor1.mp4. OpenCV leyó 654/654 fotogramas, resolución 2560×1440, FPS 29.97003, duración nominal 21.82 s.

Se generó un fragmento de 24 fotogramas reales a 640×360 para la prueba de integración. Las respuestas de YOLO/ByteTrack son **simuladas** y no deben interpretarse como detección real.

Para repetir: `SMARTRETAIL_TEST_VIDEO=/ruta/consumidor1_fragmento_24f.avi python -m pytest -q -o addopts='' tests/integration/test_user_video_pipeline.py`.

Pendiente: instalar Ultralytics, disponer de pesos y ejecutar el modelo neuronal real.
