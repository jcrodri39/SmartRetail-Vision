# Fase 4 — métricas y aislamiento por tienda

- Se corrige `dashboard`: tracks y detecciones se filtran por tienda mediante JOIN con cámara.
- Se corrige el filtro de confianza promedio de `report_data`, incluso para tiendas sin cámaras.
- `store_id=None` agrega explícitamente todas las tiendas; un ID inexistente no debe recuperar otras tiendas.
- `flujo` se define como **eventos ENTRY de zona**, no visitantes únicos ni entradas a tienda.
- `ocupacion` cuenta eventos ENTRY aún abiertos; no es un aforo validado.
- Se incluyen pruebas de regresión con dos tiendas y un evento de duración cero.

## Pendiente
- Distinguir con persistencia la salida observada y la pérdida de track.
- Definir sesiones de procesamiento para evitar colisiones de IDs y reprocesamiento duplicado.
- Evaluar ocupación por instante de referencia, eventos incompletos y deduplicación.
- Validar métricas contra anotaciones humanas y actualizar el informe académico.
