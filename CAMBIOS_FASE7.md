# Fase 7 — Selectores y corrección de mapa de calor

- Se añade selector de sesión en dashboard, reportes y mapa de calor.
- Se conserva explícitamente la opción histórica (todas las sesiones), que puede duplicar ejecuciones repetidas.
- Se valida la pertenencia de la sesión a la tienda antes de renderizar reportes.
- Se corrige la variable processing_id no definida en el endpoint /heatmap.
- Se filtran los puntos del mapa de calor por sesión.
- Los enlaces CSV/XLSX transmiten el filtro de sesión seleccionado.

Pendiente: pruebas integrales de rutas HTTP, CSRF, carga segura, videos reales y revisión APA 7.
