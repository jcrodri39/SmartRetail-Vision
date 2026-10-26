# Correcciones aplicadas — revisión parcial

1. Se eliminaron las contraseñas fijas `Admin123*` y `Analyst123*` del sembrado inicial. La creación del administrador depende de `BOOTSTRAP_ADMIN_EMAIL` y `BOOTSTRAP_ADMIN_PASSWORD` (mínimo 12 caracteres).
2. Se incorporó `SESSION_COOKIE_SECURE`, que **debe** configurarse en `true` bajo HTTPS.
3. Se documentaron las variables en `.env.example`.

## Límites y pendientes
- **No se ha corregido** el cálculo de permanencia, la lógica de tracks perdidos, la protección CSRF, los filtros por tienda ni la validación de videos.
- **No se ha demostrado** la ejecución de pruebas integrales ni la calidad de detección/tracking.
- `SECRET_KEY` todavía tiene un valor de desarrollo; **se debe configurar una clave aleatoria fuerte en `.env` antes de usar el sistema**.
- No se debe usar en producción sin revisar sesiones, autorización, protección CSRF y carga de archivos.
- Los usuarios ya existentes en una base de datos anterior no se modifican automáticamente.

## Cómo comprobar los cambios
1. Copiar `.env.example` a `.env` y configurar una clave fuerte, credenciales iniciales y HTTPS según el entorno.
2. Crear un entorno virtual y ejecutar `pip install -r requirements.txt`.
3. Ejecutar `python -m pytest -q`.
4. Verificar inicio de sesión y cierre de sesión con un usuario creado de forma controlada.
