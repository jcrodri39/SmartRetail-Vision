"""Regresión: una dependencia de visión ausente no deja la cámara en estado activo."""
import sys
from app.vision.live import LiveVision


def test_missing_ultralytics_stops_cleanly(monkeypatch):
    monkeypatch.setitem(sys.modules, "ultralytics", None)
    vision = LiveVision()
    vision.camera_id = 999999
    vision.running = True
    vision._procesar()
    assert vision.running is False
    assert vision.stats["frames"] == 0
    assert vision.latest is None
