"""Pipeline real de OpenCV + persistencia SQLite; YOLO simulado, NO valida el modelo neuronal."""
import sys
import types
from pathlib import Path
from uuid import uuid4
import cv2
import numpy as np
from app.db.database import SessionLocal, Base, engine
from app.models.entities import Tienda,Camara,Zona,Procesamiento,Track,Deteccion,EventoZona
from app.vision.live import LiveVision

class Tensor:
    def __init__(self, value): self.value=value
    def cpu(self): return self
    def tolist(self): return self.value
    def int(self): return self

class FakeBoxes:
    xyxy=Tensor([[10,10,30,60]])
    conf=Tensor([0.91])
    id=Tensor([7])

class FakeResult:
    boxes=FakeBoxes()

class FakeYOLO:
    def __init__(self, model): self.model=model
    def track(self, frame, **kwargs): return [FakeResult()]

def test_synthetic_video_to_sqlite(monkeypatch,tmp_path):
    path=tmp_path/'test.avi'
    writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'MJPG'),5.0,(80,80))
    assert writer.isOpened(),'OpenCV no pudo crear el video de prueba'
    for _ in range(3): writer.write(np.zeros((80,80,3),dtype=np.uint8))
    writer.release()
    monkeypatch.setitem(sys.modules,'ultralytics',types.SimpleNamespace(YOLO=FakeYOLO))
    Base.metadata.create_all(bind=engine)
    db=SessionLocal(); tag=uuid4().hex
    store=Tienda(nombre='Pipeline '+tag,ubicacion='Prueba')
    db.add(store);db.flush()
    camera=Camara(id_tienda=store.id_tienda,nombre='Synthetic',fuente=str(path))
    zone=Zona(id_tienda=store.id_tienda,nombre='Test Zone',coordenadas_json='[[0,0],[79,0],[79,79],[0,79]]')
    db.add_all([camera,zone]);db.commit()
    camera_id=camera.id_camara
    try:
        vision=LiveVision();vision.running=True;vision.camera_id=camera_id
        vision._procesar()
        assert vision.running is False
        db.expire_all()
        runs=db.query(Procesamiento).filter_by(id_camara=camera_id).all()
        assert len(runs)==1 and runs[0].estado=='FINISHED'
        tracks=db.query(Track).filter_by(id_procesamiento=runs[0].id_procesamiento).all()
        assert len(tracks)==1 and tracks[0].external_track_id==7
        detections=db.query(Deteccion).filter_by(id_track=tracks[0].id_track).all()
        assert len(detections)==3
        events=db.query(EventoZona).filter_by(id_track=tracks[0].id_track).all()
        assert len(events)==1
        assert events[0].motivo_cierre=='SOURCE_ENDED'
        assert events[0].permanencia_seg>=0
        assert vision.stats['frames']==3
    finally:
        runs=db.query(Procesamiento).filter_by(id_camara=camera_id).all()
        for run in runs:
            tracks=db.query(Track).filter_by(id_procesamiento=run.id_procesamiento).all()
            for track in tracks:
                db.query(EventoZona).filter_by(id_track=track.id_track).delete()
                db.query(Deteccion).filter_by(id_track=track.id_track).delete()
                db.delete(track)
            db.flush();db.delete(run)
        db.delete(zone);db.delete(camera);db.delete(store);db.commit();db.close()
