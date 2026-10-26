# Fase 16: reprocesamiento de video

- **Hallazgo:** `LiveVision` conservaba `stats`, `events` y el último fotograma entre ejecuciones. El contador de fotogramas y de entradas se acumulaba y podía distorsionar la interfaz; además `frame_index` alimentaba el reloj del video.
- **Corrección:** reinicio explícito del estado visual y los contadores al entrar a `_procesar()`. Se conservan los registros históricos de cada `Procesamiento` en SQLite.
- **Regresión:** nueva prueba con dos ejecuciones consecutivas del mismo video en la misma instancia; comprueba contadores reiniciados, sesiones independientes, tres detecciones por sesión y cierres `SOURCE_ENDED`.
- **Alcance:** se utiliza YOLO simulado; no acredita exactitud del modelo neuronal ni estabilidad en producción.
