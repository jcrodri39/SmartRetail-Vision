# Fase 20 — auditoría reproducible de video

Se añade `scripts/audit_video.py` para leer íntegramente un video, contrastar fotogramas reportados con fotogramas decodificados y calcular una medida descriptiva de variación de imagen en muestras periódicas. Se añaden dos pruebas unitarias en `tests/unit/test_audit_video.py`.

Video de usuario `consumidor1.mp4`: 654/654 fotogramas decodificados, 2560 × 1440, 29.97 FPS, 21.822 s estimados; 22 muestras (cada 30 fotogramas), diferencia media de imagen 8.9492/255. La diferencia no equivale a movimiento de personas ni a exactitud de detección.

Batería: 60 passed, 1 skipped, 43 warnings. El test omitido requiere un video externo disponible bajo la ruta esperada; la ejecución manual del video aportado se registra en `V22_diagnostico_video.json` fuera del paquete.

**No se ejecutó YOLO real**: en este entorno faltan ultralytics y pesos del modelo. No se certifica precisión, conteo ni seguimiento. El video del usuario no se redistribuye dentro del ZIP.
