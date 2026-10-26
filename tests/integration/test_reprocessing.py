"""Regresión: reprocesar el mismo video con la misma instancia no acumula contadores."""
import sys
import types
from uuid import uuid4
import cv2
import numpy as np
from app.db.database import Base, SessionLocal, engine
from app.models.entities import Tienda, Camara, Zona, Procesamiento, Track, Deteccion, EventoZona
from app.vision.live import LiveVision
from tests.integration.test_synthetic_pipeline import FakeYOLO

def test_reprocess_same_video_resets_ui_counters_but_keeps_separate_sessions(monkeypatch, tmp_path):
    path = tmp_path / "repeat.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 5.0, (80,80))
    assert writer.isOpened()
    for _ in range(3):
        writer.write(np.zeros((80,80,3), dtype=np.uint8))
    writer.release()
    monkeypatch.setitem(sys.modules, "ultralytics", types.SimpleNamespace(YOLO=FakeYOLO))
    Base.metadata.create_all(bind=engine)
    db=SessionLocal()
    store=Tienda(nombre="Repeat "+uuid4().hex, ubicacion="Prueba")
    db.add(store); db.flush()
    cam=Camara(id_tienda=store.id_tienda,nombre="Repeat",fuente=str(path))
    zone=Zona(id_tienda=store.id_tienda,nombre="Zone",coordenadas_json="[[0,0],[79,0],[79,79],[0,79]]")
    db.add_all([cam,zone]); db.commit()
    try:
        vision=LiveVision(); vision.camera_id=cam.id_camara
        for _ in range(2):
            vision.running=True
            vision._procesar()
            assert vision.stats["frames"]==3
            assert vision.stats["tracks"]==1
            assert vision.stats["entries"]==1
            assert vision.stats["exits"]==0
            assert len(vision.events)==1
        db.expire_all()
        runs=db.query(Procesamiento).filter_by(id_camara=cam.id_camara).all()
        assert len(runs)==2
        assert len({r.id_procesamiento for r in runs})==2
        assert all(r.estado=="FINISHED" for r in runs)
        for run in runs:
            tracks=db.query(Track).filter_by(id_procesamiento=run.id_procesamiento).all()
            assert len(tracks)==1
            assert len(db.query(Deteccion).filter_by(id_track=tracks[0].id_track).all())==3
            events=db.query(EventoZona).filter_by(id_track=tracks[0].id_track).all()
            assert len(events)==1 and events[0].motivo_cierre=="SOURCE_ENDED"
    finally:
        for run in db.query(Procesamiento).filter_by(id_camara=cam.id_camara).all():
            for tr in db.query(Track).filter_by(id_procesamiento=run.id_procesamiento).all():
                db.query(EventoZona).filter_by(id_track=tr.id_track).delete()
                db.query(Deteccion).filter_by(id_track=tr.id_track).delete()
                db.delete(tr)
            db.flush(); db.delete(run)
        db.delete(zone); db.delete(cam); db.delete(store); db.commit(); db.close()
