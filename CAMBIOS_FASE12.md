# Fase 12: integración HTTP verificable

## Cambios
- `app/core/security.py`: adaptador Argon2id basado en `argon2-cffi` cuando `pwdlib` no está disponible. Conserva el formato PHC de hashes Argon2; no garantiza compatibilidad con algoritmos diferentes.
- `requirements.txt`: explicita `argon2-cffi`.
- `tests/integration/test_pages.py`: corrige el encabezado Origin para pruebas POST legítimas y añade pruebas HTTP de origen externo, origen ausente, inicio de sesión real, dashboard autenticado y cierre de sesión.

## Comando ejecutado
`python -m pytest -q -o addopts='' tests/unit tests/integration`

## Resultado
45 passed, 16 warnings in 1.51s (Python 3.13, entorno de evaluación).

## Límites
- No se ejecutó YOLO/ByteTrack: `ultralytics` no está instalado.
- Las pruebas se ejecutaron con TestClient, no con navegador gráfico ni servidor remoto.
- Las advertencias incluyen `datetime.utcnow`, el ciclo de vida FastAPI `on_event`, y una clave JWT de desarrollo inferior a 32 bytes.
- La defensa Origin/Referer no sustituye tokens CSRF por sesión.
- Antes de desplegar: establecer SECRET_KEY aleatoria >=32 bytes, HTTPS, SESSION_COOKIE_SECURE=true, SMARTRETAIL_PUBLIC_ORIGIN correcto, y ejecutar migraciones y pruebas con datos representativos.
