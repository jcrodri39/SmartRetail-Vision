# Fase 8 — V11: reparación de rutas y controles de carga

Fecha: 2026-10-23.

## Cambios verificados
- `app/web/routes/pages.py`: se añadieron importaciones que faltaban de `live`, `report_data`, `make_csv`, `make_xlsx` y `MIME_XLSX`. Antes podían producir errores `NameError` al solicitar visión, reportes o descargas.
- La carga de video ahora lee bloques de 1 MiB, limita la carga a 100 MiB, rechaza archivos vacíos y elimina archivos parciales cuando ocurre un error. **No se ha añadido validación real del códec/contenido**, solo de extensión.
- Las operaciones de activación/desactivación y eliminación de cámaras, zonas y usuarios ahora responden 404 cuando el registro no existe. La modificación de rol rechaza roles no reconocidos.
- Se añadieron tres pruebas de regresión **estáticas** sobre el código fuente. No son pruebas HTTP ni prueban la interfaz visual.

## Ejecución
`python -m pytest -q -o addopts='' tests/unit`: 27 passed, 12 warnings (12 advertencias por `datetime.utcnow()`). `python -m compileall -q app`: correcto.

## Limitaciones
No se pudieron realizar pruebas HTTP reales en este entorno porque falta `pwdlib` y la instalación desde el índice de paquetes no tuvo acceso a red. También falta `ultralytics` para ejecutar visión artificial. No afirmar que la suite completa o la integración end-to-end pasó. Sigue pendiente CSRF, validación de contenidos, pruebas de carga y comprobación de las rutas reales en TestClient. El límite de 100 MiB es una medida parcial: se recomienda además aplicar límites de petición en el proxy.
