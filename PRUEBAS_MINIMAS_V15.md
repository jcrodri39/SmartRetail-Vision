# Evidencia de funcionamiento mínimo — V15

Prueba HTTP real con `fastapi.testclient.TestClient` y registros SQLite de prueba:

1. Crea usuario administrador, tienda, cámara, zona, sesión, trayectoria, detección y evento.
2. Autentica al usuario por POST `/login`.
3. Comprueba HTTP 200 en `/dashboard`, `/reports` y `/heatmap` filtrados por tienda y sesión.
4. Comprueba `/reports/data` con exactamente 1 trayectoria y 1 detección.
5. Descarga CSV y verifica que contiene el nombre de la zona.
6. Descarga XLSX y verifica que es un archivo Office Open XML válido con `xl/workbook.xml`.
7. Rechaza un ID de sesión inexistente.
8. Elimina los registros de prueba.

Ejecutar: `python -m pytest -q -o addopts='' tests/unit tests/integration`

**Alcance:** demuestra un flujo mínimo de web + autenticación + base de datos + indicadores + exportaciones; no demuestra procesamiento de vídeo con YOLO/ByteTrack, interfaz visual en navegador ni despliegue en máquina destino.

**Riesgos pendientes:** clave JWT de desarrollo corta, uso de `datetime.utcnow`, verificación real del contenido de archivos subidos y CSRF basado solo en cabeceras de origen.
