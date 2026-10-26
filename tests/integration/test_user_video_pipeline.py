"""Real user video frames, but synthetic YOLO output: NOT a real model validation."""
import os
from pathlib import Path
import pytest
from tests.integration.test_synthetic_pipeline import FakeYOLO
import sys, types
from uuid import uuid4
from app.db.database import SessionLocal,Base,engine
from app.models.entities import Tienda,Camara,Zona,Procesamiento,Track,Deteccion,EventoZona
from app.vision.live import LiveVision

@pytest.mark.integration
def test_user_video_opencv_to_sqlite(monkeypatch):
    video=os.environ.get("SMARTRETAIL_TEST_VIDEO")
    if not video or not Path(video).is_file():
        pytest.skip("Definir SMARTRETAIL_TEST_VIDEO para probar video del usuario")
    monkeypatch.setitem(sys.modules,"ultralytics",types.SimpleNamespace(YOLO=FakeYOLO))
    Base.metadata.create_all(bind=engine)
    db=SessionLocal();tag=uuid4().hex
    store=Tienda(nombre="Real video frames "+tag,ubicacion="Test")
    db.add(store);db.flush()
    camera=Camara(id_tienda=store.id_tienda,nombre="User video",fuente=video)
    zone=Zona(id_tienda=store.id_tienda,nombre="Frame zone",coordenadas_json="[[0,0],[639,0],[639,359],[0,359]]")
    db.add_all([camera,zone]);db.commit();camera_id=camera.id_camara
    try:
        vision=LiveVision();vision.running=True;vision.camera_id=camera_id;vision._procesar()
        assert not vision.running
        db.expire_all()
        runs=db.query(Procesamiento).filter_by(id_camara=camera_id).all()
        assert len(runs)==1 and runs[0].estado=="FINISHED"
        tracks=db.query(Track).filter_by(id_procesamiento=runs[0].id_procesamiento).all()
        assert len(tracks)==1
        detections=db.query(Deteccion).filter_by(id_track=tracks[0].id_track).all()
        assert len(detections)==24
        events=db.query(EventoZona).filter_by(id_track=tracks[0].id_track).all()
        assert len(events)==1 and events[0].motivo_cierre=="SOURCE_ENDED"
        assert vision.stats["frames"]==24
    finally:
        runs=db.query(Procesamiento).filter_by(id_camara=camera_id).all()
        for run in runs:
            tracks=db.query(Track).filter_by(id_procesamiento=run.id_procesamiento).all()
            for tr in tracks:
                db.query(EventoZona).filter_by(id_track=tr.id_track).delete()
                db.query(Deteccion).filter_by(id_track=tr.id_track).delete()
                db.delete(tr)
            db.flush();db.delete(run)
        db.delete(zone);db.delete(camera);db.delete(store);db.commit();db.close()
