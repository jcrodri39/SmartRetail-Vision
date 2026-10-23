# Pruebas
`pytest`
- unit: geometría y métricas;
- security: hashing/JWT;
- integration: login, health, protección de páginas;
- functional: catálogo UC001–UC008;
- vision: ciclo de vida del monitor.
Añadir en producción pruebas E2E Playwright, carga, RTSP/reconexión y benchmark con dataset etiquetado. No se inventa mAP/precision/recall.
- unit (V5): `test_logging_config.py` (filtro de privacidad, contexto de sesión, appenders, rendimiento) y
  `test_excel_report.py` (hojas, fórmulas, KPIs, reporte vacío).
