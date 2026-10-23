"""
Bitácora de SmartRetail Vision: equivalente en Python de LogBack.

Equivalencias (LogBack en Java  ->  logging, biblioteca estándar de Python):
    logback.xml                         -> diccionario + logging.config.dictConfig
    LoggerFactory.getLogger(Clase)      -> logging.getLogger("smartretail.modulo")
    ConsoleAppender                     -> logging.StreamHandler
    RollingFileAppender (por tamaño)    -> logging.handlers.RotatingFileHandler
    RollingFileAppender (por día)       -> logging.handlers.TimedRotatingFileHandler
    AsyncAppender                       -> logging.handlers.QueueHandler + QueueListener
    PatternLayout "%d %-5level %logger" -> logging.Formatter("%(asctime)s %(levelname)-8s %(name)s")
    Filter / ThresholdFilter            -> logging.Filter / nivel del handler
    MDC.put("sesion", id)               -> contextvars.ContextVar + Filter
    additivity="false"                  -> "propagate": False

Compatible con Python 3.11 (versión fijada en .python-version del proyecto).
"""
from __future__ import annotations

import atexit
import contextvars
import logging
import logging.config
import logging.handlers
import queue
import re
import time
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

# ---------------------------------------------------------------------------
# 1. Contexto de sesión (equivalente al MDC de LogBack)
# ---------------------------------------------------------------------------
id_sesion_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("id_sesion", default="-")


@contextmanager
def sesion_log(id_sesion: str) -> Iterator[None]:
    """Todas las líneas emitidas dentro del bloque llevan este id de sesión."""
    token = id_sesion_ctx.set(id_sesion)
    try:
        yield
    finally:
        id_sesion_ctx.reset(token)


class ContextoSesionFilter(logging.Filter):
    """Agrega record.id_sesion. No lo sobrescribe si ya viene capturado
    (el valor se toma en el hilo que emite, antes de pasar por la cola)."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "id_sesion"):
            record.id_sesion = id_sesion_ctx.get()
        return True


# ---------------------------------------------------------------------------
# 2. Filtro de privacidad (RNF006)
# ---------------------------------------------------------------------------
class PrivacidadFilter(logging.Filter):
    """Enmascara credenciales de fuentes RTSP/HTTP (rtsp://usuario:clave@ip)
    y la parte local de los correos de usuarios antes de escribir el log."""

    _URL_CON_CREDENCIALES = re.compile(r"(?P<esquema>[a-zA-Z][a-zA-Z0-9+.-]*://)[^:/@\s]+:[^@/\s]+@")
    _CORREO = re.compile(r"\b[\w.+-]+@(?P<dominio>[\w-]+(?:\.[\w-]+)+)\b")

    @classmethod
    def limpiar(cls, texto: str) -> str:
        texto = cls._URL_CON_CREDENCIALES.sub(r"\g<esquema>***:***@", texto)
        return cls._CORREO.sub(r"***@\g<dominio>", texto)

    def filter(self, record: logging.LogRecord) -> bool:
        mensaje = record.getMessage()
        limpio = self.limpiar(mensaje)
        if limpio != mensaje:
            record.msg, record.args = limpio, None
        return True


# ---------------------------------------------------------------------------
# 3. Configuración declarativa (equivalente a logback.xml)
# ---------------------------------------------------------------------------
FORMATO_CONSOLA = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
FORMATO_ARCHIVO = ("%(asctime)s | %(levelname)-8s | sesion=%(id_sesion)s | "
                   "%(name)s:%(funcName)s:%(lineno)d | %(message)s")
FORMATO_RENDIMIENTO = "%(asctime)s;%(id_sesion)s;%(message)s"

LOGGER_DESTINOS = "_destinos_smartretail"
_listener: logging.handlers.QueueListener | None = None


def construir_configuracion(dir_logs: str | Path = "logs", nivel: str = "INFO") -> dict:
    dir_logs = Path(dir_logs)
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "contexto": {"()": ContextoSesionFilter},
            "privacidad": {"()": PrivacidadFilter},
        },
        "formatters": {
            "consola": {"format": FORMATO_CONSOLA, "datefmt": "%H:%M:%S"},
            "archivo": {"format": FORMATO_ARCHIVO},
            "rendimiento": {"format": FORMATO_RENDIMIENTO},
        },
        "handlers": {
            "consola": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout",
                        "level": nivel, "formatter": "consola"},
            "consola_app": {"class": "logging.StreamHandler", "stream": "ext://sys.stdout",
                            "level": nivel, "formatter": "consola"},
            "archivo_app": {"class": "logging.handlers.RotatingFileHandler",
                            "filename": str(dir_logs / "smartretail.log"),
                            "maxBytes": 5 * 1024 * 1024, "backupCount": 5, "encoding": "utf-8",
                            "level": "DEBUG", "formatter": "archivo", "filters": ["contexto"]},
            "archivo_errores": {"class": "logging.handlers.TimedRotatingFileHandler",
                                "filename": str(dir_logs / "errores.log"),
                                "when": "midnight", "backupCount": 30, "encoding": "utf-8",
                                "level": "ERROR", "formatter": "archivo", "filters": ["contexto"]},
            "archivo_rendimiento": {"class": "logging.handlers.RotatingFileHandler",
                                    "filename": str(dir_logs / "rendimiento.csv"),
                                    "maxBytes": 5 * 1024 * 1024, "backupCount": 3, "encoding": "utf-8",
                                    "formatter": "rendimiento", "filters": ["contexto"]},
        },
        "loggers": {
            # "smartretail" escribe en una cola (ver configurar_logging); sus destinos
            # reales se declaran aquí, en un logger auxiliar que nunca recibe mensajes.
            "smartretail": {"level": "DEBUG", "handlers": [], "propagate": False},
            LOGGER_DESTINOS: {"level": "CRITICAL", "propagate": False,
                              "handlers": ["consola_app", "archivo_app", "archivo_errores"]},
            "smartretail.rendimiento": {"level": "INFO", "handlers": ["archivo_rendimiento"],
                                        "propagate": False},
            "uvicorn.error": {"level": "INFO"},
        },
        "root": {"level": "WARNING", "handlers": ["consola"]},
    }


def configurar_logging(dir_logs: str | Path = "logs", nivel: str = "INFO") -> None:
    """Aplica la configuración y monta el envío asíncrono (AsyncAppender):
    el hilo de visión solo encola el registro; un hilo aparte escribe en disco."""
    global _listener
    if _listener is not None:
        return  # idempotente: uvicorn --reload puede importar dos veces
    Path(dir_logs).mkdir(parents=True, exist_ok=True)
    logging.config.dictConfig(construir_configuracion(dir_logs, nivel))

    # dictConfig creó los destinos y los dejó en el logger auxiliar "_destinos";
    # se retiran de ahí y se entregan al hilo escritor (QueueListener).
    auxiliar = logging.getLogger(LOGGER_DESTINOS)
    destinos = list(auxiliar.handlers)
    for h in destinos:
        auxiliar.removeHandler(h)

    cola: queue.Queue = queue.Queue(-1)
    manejador_cola = logging.handlers.QueueHandler(cola)
    manejador_cola.addFilter(ContextoSesionFilter())   # captura el contexto antes de encolar
    manejador_cola.addFilter(PrivacidadFilter())       # nada sensible entra a la cola
    logging.getLogger("smartretail").addHandler(manejador_cola)

    _listener = logging.handlers.QueueListener(cola, *destinos, respect_handler_level=True)
    _listener.start()
    atexit.register(detener_logging)


def detener_logging() -> None:
    """Vacía la cola y cierra los archivos."""
    global _listener
    if _listener is not None:
        _listener.stop()
        _listener = None


# ---------------------------------------------------------------------------
# 4. Medición de rendimiento (RNF001): FPS y latencia por bloque de frames
# ---------------------------------------------------------------------------
class RegistroRendimiento:
    """Acumula tiempos por etapa y escribe una fila CSV cada `cada_n_frames`
    cuadros, para no escribir en disco en cada frame."""

    def __init__(self, cada_n_frames: int = 100) -> None:
        self.cada_n_frames = cada_n_frames
        self._log = logging.getLogger("smartretail.rendimiento")
        self._tiempos: dict[str, float] = defaultdict(float)
        self._frames = 0
        self._personas = 0
        self._inicio = time.perf_counter()

    @contextmanager
    def medir(self, etapa: str) -> Iterator[None]:
        t0 = time.perf_counter()
        try:
            yield
        finally:
            self._tiempos[etapa] += time.perf_counter() - t0

    def frame_procesado(self, personas: int = 0) -> None:
        self._frames += 1
        self._personas += personas
        if self._frames >= self.cada_n_frames:
            self.volcar()

    def volcar(self) -> None:
        if self._frames == 0:
            return
        transcurrido = time.perf_counter() - self._inicio
        fps = self._frames / transcurrido if transcurrido > 0 else 0.0
        latencias = ";".join(f"{e}={1000 * t / self._frames:.1f}ms" for e, t in sorted(self._tiempos.items()))
        self._log.info("frames=%d;fps=%.2f;personas_prom=%.1f;%s",
                       self._frames, fps, self._personas / self._frames, latencias)
        self._tiempos.clear()
        self._frames = self._personas = 0
        self._inicio = time.perf_counter()
