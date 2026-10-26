"""La cámara no permite dos trabajadores simultáneos ni reinicio prematuro."""
import threading
from app.vision.live import LiveVision


def test_second_start_rejected_until_worker_finishes(monkeypatch):
    entered=threading.Event()
    release=threading.Event()
    vision=LiveVision()
    def fake_processing():
        entered.set()
        assert release.wait(5)
    monkeypatch.setattr(vision,"_procesar",fake_processing)
    assert vision.start(1) is True
    try:
        assert entered.wait(5)
        assert vision.start(2) is False
        assert vision.camera_id==1
        vision.stop()
        assert vision.start(2) is False  # stop() no implica que el worker terminó
    finally:
        release.set()
        vision._thread.join(timeout=5)
    assert not vision._thread.is_alive()
    assert vision.start(2) is True
    vision._thread.join(timeout=5)
    assert vision.camera_id==2
    assert vision.running is False


def test_thread_start_failure_does_not_leave_running(monkeypatch):
    vision=LiveVision()
    def fail(_):
        raise RuntimeError("No se pudo crear el hilo")
    monkeypatch.setattr(threading.Thread,"start",fail)
    import pytest
    with pytest.raises(RuntimeError):
        vision.start(7)
    assert vision.running is False
    assert vision._thread is None
