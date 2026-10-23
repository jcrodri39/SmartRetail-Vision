# Librerías aplicadas · Clase 10 (Recursos Java)

El proyecto está en Python, por lo que se aplicó la **funcionalidad equivalente** de 2 librerías revisadas.

## 1. Apache POI → openpyxl (reporte Excel, UC007)
- Servicio: `app/services/excel_report.py` (`build_workbook`, `make_xlsx`).
- Ruta: `GET /reports/download.xlsx?store_id=…` · botón en `/reports`.
- Reutiliza `report_data()`: CSV, vista web y Excel muestran las mismas cifras.
- Hojas: Resumen (KPIs con fórmulas), Zonas (tabla + gráfico de barras + escala de color),
  Flujo por hora (tabla dinámica + gráfico de líneas), Eventos (detalle anónimo), Trazabilidad (parámetros YOLO/tracker).
- Cada exportación se registra en la tabla `reporte` con tipo `XLSX_ANALYTICS`.

## 2. LogBack → logging (bitácora)
- Configuración: `app/core/logging_config.py` (equivalente a `logback.xml`), se activa en `app/main.py`.
- Destinos: consola, `logs/smartretail.log` (rotación por tamaño), `logs/errores.log` (rotación diaria, solo ERROR),
  `logs/rendimiento.csv` (FPS/latencia, logger con `propagate=False`).
- Escritura asíncrona con `QueueHandler`/`QueueListener` (como `AsyncAppender`): el hilo de YOLO no espera al disco.
- `PrivacidadFilter`: enmascara `rtsp://usuario:clave@` y correos antes de escribir (RNF006).
- `sesion_log()`: equivalente al MDC; cada línea lleva `sesion=camX-fecha`.
- Variables `.env`: `LOG_DIR`, `LOG_LEVEL`.
