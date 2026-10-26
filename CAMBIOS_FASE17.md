# Fase 17 — Fallo de dependencia de YOLO

**Problema:** `from ultralytics import YOLO` estaba fuera de los manejadores de error de `_procesar()`. Si faltaba la dependencia, el hilo podía terminar con excepción dejando `running=True` y aparentando una ejecución activa.

**Corrección:** se captura `ImportError`, se registra la causa, se restablece `running=False` y se abandona el procesamiento sin inventar detecciones.

**Prueba nueva:** `tests/unit/test_missing_ultralytics.py`, que fuerza la ausencia de `ultralytics` y verifica el estado de la instancia.

**Límite:** esta prueba no ejecuta YOLO real; para validar detección se necesitan la biblioteca, los pesos del modelo y un video de referencia.
