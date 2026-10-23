# SmartRetail Vision V5 — COMPLETO
Python 3.11.9 + FastAPI + SQLAlchemy 2 + YOLO + ByteTrack + OpenCV.

## Casos de uso
UC001 Login/logout; UC002 fuentes de video; UC003 editor visual de zonas; UC004 YOLO Live; UC005 dashboard; UC006 heatmap; UC007 reportes CSV y Excel; UC008 usuarios/roles.

## Ejecutar
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload

Abrir: http://127.0.0.1:8000/login

Admin: admin@smartretail.local / Admin123*
Analista: analyst@smartretail.local / Analyst123*

En Fuentes de video registre `0` para webcam, una ruta MP4 o un RTSP autorizado. Configure una zona y luego abra YOLO Live.

## Privacidad
Sin reconocimiento facial. IDs temporales de tracking. No se infiere identidad nominal.

## Librerías aplicadas (Clase 10: Recursos Java → equivalentes Python)
| Librería Java | Equivalente Python | Dónde se aplica |
|---|---|---|
| Apache POI | `openpyxl` | `app/services/excel_report.py` · ruta `/reports/download.xlsx` · botón "Exportar reporte Excel" |
| LogBack | `logging` (estándar) | `app/core/logging_config.py` · usado en `main.py`, `auth.py`, `pages.py`, `vision/live.py` |

Bitácoras generadas en `logs/`: `smartretail.log` (rotación 5 MB × 5), `errores.log` (diaria, 30 días) y
`rendimiento.csv` (FPS y latencia por bloque de 100 frames). Demo sin cámara: `python -m scripts.demo_librerias`.
Detalle en `docs/LIBRERIAS.md`.
