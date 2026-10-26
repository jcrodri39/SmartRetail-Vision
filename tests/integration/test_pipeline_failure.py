"""Prueba de fallo en inferencia: persiste sesión FAILED y cierra eventos sin inventar salidas."""
import sys
import types
from uuid import uuid4

import cv2
import numpy as np

from app.db.database import Base, SessionLocal, engine
from app.models.entities import Tienda, Camara, Zona, Procesamiento, Track, Deteccion, EventoZona
from app.vision.live import LiveVision
from tests.integration.test_synthetic_pipeline import FakeResult


class FailingYOLO:
    def __init__(self, model):
        self.calls = 0

    def track(self, frame, **kwargs):
        self.calls += 1
        if self.calls == 2:
            raise RuntimeError('fallo simulado del motor de inferencia')
        return [FakeResult()]


def test_error_during_inference_marks_failed_and_closes_observations(monkeypatch, tmp_path):
    path = tmp_path / 'failure.avi'
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*'MJPG'), 5.0, (80, 80))
    assert writer.isOpened()
    for _ in range(3):
        writer.write(np.zeros((80, 80, 3), dtype=np.uint8))
    writer.release()
    monkeypatch.setitem(sys.modules, 'ultralytics', types.SimpleNamespace(YOLO=FailingYOLO))
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    tag = uuid4().hex
    store = Tienda(nombre='Failure ' + tag, ubicacion='Prueba')
    db.add(store)
    db.flush()
    camera = Camara(id_tienda=store.id_tienda, nombre='Failure test', fuente=str(path))
    zone = Zona(id_tienda=store.id_tienda, nombre='Zona', coordenadas_json='[[0,0],[79,0],[79,79],[0,79]]')
    db.add_all([camera, zone])
    db.commit()
    try:
        vision = LiveVision()
        vision.camera_id = camera.id_camara
        vision.running = True
        vision._procesar()
        db.expire_all()
        runs = db.query(Procesamiento).filter_by(id_camara=camera.id_camara).all()
        assert len(runs) == 1
        assert runs[0].estado == 'FAILED'
        assert runs[0].fin is not None
        tracks = db.query(Track).filter_by(id_procesamiento=runs[0].id_procesamiento).all()
        assert len(tracks) == 1
        detections = db.query(Deteccion).filter_by(id_track=tracks[0].id_track).all()
        assert len(detections) == 1
        events = db.query(EventoZona).filter_by(id_track=tracks[0].id_track).all()
        assert len(events) == 1
        assert events[0].motivo_cierre == 'ERROR'
        assert events[0].salida is not None
        assert events[0].permanencia_seg >= 0
        assert vision.running is False
    finally:
        for run in db.query(Procesamiento).filter_by(id_camara=camera.id_camara).all():
            for track in db.query(Track).filter_by(id_procesamiento=run.id_procesamiento).all():
                db.query(EventoZona).filter_by(id_track=track.id_track).delete()
                db.query(Deteccion).filter_by(id_track=track.id_track).delete()
                db.delete(track)
            db.flush()
            db.delete(run)
        db.delete(zone)
        db.delete(camera)
        db.delete(store)
        db.commit()
        db.close()
