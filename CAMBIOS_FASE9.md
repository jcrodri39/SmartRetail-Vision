# Fase 9 — Validaciones de integridad y usuarios

## Cambios realizados
- `POST /videos`: rechaza una tienda inexistente (HTTP 404) antes de crear una cámara.
- `POST /videos/upload`: rechaza una tienda inexistente (HTTP 404) antes de escribir el archivo.
- `POST /zones`: rechaza una tienda inexistente (HTTP 404).
- `POST /users`: valida el rol `ADMIN` o `ANALYST`, exige contraseñas de al menos 12 caracteres y rechaza correos ya existentes con HTTP 409.

## Comprobaciones ejecutadas
- `python -m compileall -q app`: correcto.
- `python -m pytest -q -o addopts='' tests/unit`: 27 passed, 12 warnings (advertencias de `datetime.utcnow`).

## Límites de la evidencia
- No se ejecutaron pruebas HTTP reales: falta `pwdlib` para importar la aplicación completa en este entorno.
- Estas validaciones son controles de aplicación y no sustituyen restricciones de integridad de la base de datos ni pruebas de concurrencia.
- La protección CSRF, el control de tipos de archivo por contenido, la validación de videos reales, la suite de integración y la actualización del informe Word siguen pendientes.
- No hay evidencia nueva de precisión de YOLO ni del porcentaje de rúbrica alcanzado.
