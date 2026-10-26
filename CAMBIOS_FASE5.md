# Fase 5 — V8: sesiones y cierres observacionales

- Nueva tabla `procesamiento` para distinguir ejecuciones de una misma cámara.
- `track.id_procesamiento` enlaza cada trayectoria con su ejecución.
- `evento_zona.motivo_cierre` distingue `OBSERVED_EXIT`, `TRACK_LOST`, `SOURCE_ENDED`, `STOPPED` y `ERROR`.
- Se añaden pruebas unitarias de reutilización de identificadores y motivos de cierre.

**Advertencia de migración:** SQLAlchemy `create_all()` NO agrega columnas a tablas existentes. Para datos previos, ejecutar una migración respaldada antes de iniciar V8. La herramienta incluida solo realiza migración aditiva SQLite; se debe respaldar la base antes de usarla. Las sesiones anteriores permanecerán nulas (desconocidas), no se inventa su procedencia.

**Limitaciones:** el cierre por pérdida no demuestra salida física; la ocupación basada en eventos abiertos no es un aforo validado; falta la validación extremo a extremo y la verificación de GitHub. Esta fase no modifica el informe Word.
