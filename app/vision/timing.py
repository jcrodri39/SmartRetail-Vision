"""Reloj de eventos: distingue tiempo de video y tiempo de procesamiento."""
from datetime import datetime, timedelta
import math

class VideoClock:
    """Ancla timestamps de video a una fecha de sesión, sin usar velocidad de inferencia."""
    def __init__(self, started_at: datetime, fps: float, is_file: bool):
        self.started_at = started_at
        self.fps = fps if math.isfinite(fps) and fps > 0 else None
        self.is_file = is_file
        self.previous = 0.0

    def at_frame(self, frame_index: int, position_ms: float | None = None, live_elapsed: float | None = None) -> datetime:
        if self.is_file:
            # POS_MSEC puede ser cero o inconsistente según el contenedor/decodificador.
            from_frame = (frame_index - 1) / self.fps if self.fps else None
            pos = position_ms / 1000 if position_ms is not None and math.isfinite(position_ms) and position_ms >= 0 else None
            if pos is not None and (frame_index == 1 or pos > self.previous):
                seconds = pos
            elif from_frame is not None:
                seconds = from_frame
            else:
                raise ValueError("El video no proporciona timestamps ni FPS válido")
        else:
            if live_elapsed is None or not math.isfinite(live_elapsed):
                raise ValueError("Se requiere tiempo monotónico para fuente en vivo")
            seconds = max(0.0, live_elapsed)
        seconds = max(seconds, self.previous)
        self.previous = seconds
        return self.started_at + timedelta(seconds=seconds)

def close_at_last_seen(event, last_seen: datetime, reason: str = "TRACK_LOST"):
    if reason not in {"TRACK_LOST", "SOURCE_ENDED", "STOPPED", "ERROR"}:
        raise ValueError("Motivo de cierre no válido")
    """Cierra la observación al último instante visible, no al fin de la ejecución."""
    event.salida = max(event.entrada, last_seen)
    event.permanencia_seg = (event.salida - event.entrada).total_seconds()

    event.motivo_cierre = reason
