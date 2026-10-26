# Fase 15 — tolerancia a fallos del pipeline

Se añadió `tests/integration/test_pipeline_failure.py`, que crea un video AVI real de tres fotogramas con OpenCV, simula una detección válida y fuerza una excepción del motor YOLO en el segundo fotograma.

La prueba comprueba que la sesión se marca `FAILED`, que conserva la detección del primer fotograma, que el evento abierto se cierra con `motivo_cierre=ERROR` (no `OBSERVED_EXIT`), que existe una fecha de finalización y que el motor deja de estar ejecutándose. Usa una base SQLite real y limpia los registros generados.

Se ejecutaron todas las pruebas en `tests/` y `compileall`. Esta prueba NO demuestra precisión ni ejecución real del modelo YOLO o ByteTrack: ambos se sustituyen por dobles de prueba. Continúan pendientes las pruebas con pesos del modelo y videos reales de personas, la interfaz en navegador y el despliegue en el equipo final.

Consultar `V17_resultados.txt` fuera del paquete para el resumen de pytest.
