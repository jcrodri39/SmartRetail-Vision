# Fase 14 — Prueba del pipeline con video sintético

Se agregó `tests/integration/test_synthetic_pipeline.py`.

La prueba crea un archivo AVI de tres fotogramas con OpenCV, sustituye **exclusivamente el detector YOLO/ByteTrack** por una respuesta determinista (ID temporal 7, confianza 0.91) y ejecuta el método de producción `LiveVision._procesar()`. Comprueba persistencia real en SQLite: una sesión finalizada, un track, tres detecciones y un evento de zona cerrado con `SOURCE_ENDED`.

**No se ha probado la precisión de YOLO ni ByteTrack reales**, ni una cámara física. La prueba verifica el flujo de video, orquestación, análisis de zonas y escritura a la base de datos bajo detecciones simuladas. La prueba usa `Base.metadata.create_all` en una base de prueba y limpia los registros generados.

Ejecutar: `python -m pytest -q -o addopts='' tests/integration/test_synthetic_pipeline.py`.

Resultado global: consultar `V16_resultados.txt` adjunto. Persisten advertencias por `datetime.utcnow`.
