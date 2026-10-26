# Fase 10 — V13: defensa de origen en escrituras HTTP

- Middleware para bloquear POST/PUT/PATCH/DELETE sin Origin o Referer del mismo origen.
- Rechaza `Origin: null`, esquemas diferentes y orígenes externos.
- En despliegue detrás de proxy definir `SMARTRETAIL_PUBLIC_ORIGIN=https://dominio-publico`.
- **Limitación:** validación Origin/Referer no sustituye tokens CSRF por sesión; clientes que omiten ambos encabezados recibirán 403.
- **No se han probado las rutas reales HTTP**, pues faltan `pwdlib` y `ultralytics` en el entorno.
- Se recomienda añadir tokens CSRF, tests de integración y pruebas reales de YOLO antes de producción.
