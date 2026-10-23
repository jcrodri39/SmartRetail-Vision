# Trazabilidad funcional V4
| UC | Flujo web ejecutable | Backend/Dominio | Resultado |
|---|---|---|---|
| UC001 Iniciar sesión | `/login`, `/logout` | JWT cookie + Argon2 + Usuario | Acceso por sesión |
| UC002 Gestionar video | `/videos` | Camara + upload/toggle | Fuente configurada |
| UC003 Configurar zonas | `/zones` | editor canvas + ZoneEngine | Polígonos activos |
| UC004 Procesar video | `/vision` | OpenCV + YOLO + ByteTrack + DB | Detecciones/tracks/eventos |
| UC005 Dashboard | `/dashboard` | Metrics service | KPIs por zona |
| UC006 Mapa de calor | `/heatmap` | centroides Deteccion | concentración espacial |
| UC007 Reportes | `/reports` | CSV + Reporte | salida consolidada |
| UC008 Usuarios | `/users` | Usuario + roles + estado | usuarios/roles actualizados |


## UC007 V4.1
El módulo de reportes ahora consolida flujo, permanencia, ocupación, visitas completadas, tracks, detecciones, confianza media YOLO, ranking por zona, insights, detalle operativo, historial, exportación CSV e impresión/PDF del navegador.

## V5 · Librerías equivalentes (Clase 10)
| Requisito | Librería (Java → Python) | Implementación | Prueba |
|---|---|---|---|
| RF011 / UC007 Generar reportes | Apache POI → openpyxl | `excel_report.make_xlsx`, `/reports/download.xlsx` | `tests/unit/test_excel_report.py` |
| RNF001 Rendimiento (FPS/latencia) | LogBack → logging | `RegistroRendimiento` en `vision/live.py` → `logs/rendimiento.csv` | `test_registro_rendimiento_escribe_fps_y_latencia` |
| RNF006 Privacidad | LogBack → logging | `PrivacidadFilter` (RTSP y correos enmascarados) | `test_enmascara_*` |
| UC004 flujos 1A/2A (registrar incidencia) | LogBack → logging | `log.error/warning/exception` en `vision/live.py` | demo `scripts/demo_librerias.py` |
| Trazabilidad de sesión de procesamiento | LogBack (MDC) → contextvars | `sesion_log()` · campo `sesion=` en cada línea | `test_contexto_de_sesion_por_hilo` |
