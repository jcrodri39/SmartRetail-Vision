# Fase 3 — Corrección temporal (parcial)

- Nuevo `app/vision/timing.py`: reloj separado para archivos de video y fuentes en vivo.
- `app/vision/live.py`: duración de eventos calculada con tiempo de video; fallback FPS si POS_MSEC no progresa.
- Tracks perdidos: cierre al último instante observado tras tolerancia de 1 segundo; cierre final también al último instante observado.
- Punto espacial: centro inferior de la caja para la pertenencia a zona.
- Nuevas pruebas unitarias en `tests/unit/test_video_timing.py`.

## Limitaciones pendientes

- No se ha validado en videos reales ni medido precisión.
- La tabla EventoZona no registra motivo de cierre ni calidad de la observación: una salida real y una pérdida siguen siendo indistinguibles en BD.
- Para videos con FPS variable, POS_MSEC del decodificador debe validarse frente a timestamps de presentación; el fallback a FPS promedio puede sesgar medidas.
- No se ha corregido concurrencia global, multi-tienda, CSRF ni carga de archivos.
- Para demostrar TDD hace falta historial verificable de pruebas previas a implementación.
