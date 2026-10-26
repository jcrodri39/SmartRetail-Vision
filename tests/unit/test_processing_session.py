from datetime import datetime, timedelta
from types import SimpleNamespace
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.db.database import Base
from app.models.entities import Camara, Tienda, Procesamiento, Track, Zona, EventoZona
from app.vision.timing import close_at_last_seen


def test_closure_reasons_are_distinct():
    a=datetime(2026,1,1)
    ev=SimpleNamespace(entrada=a,salida=None,permanencia_seg=0,motivo_cierre=None)
    close_at_last_seen(ev,a+timedelta(seconds=3),reason="TRACK_LOST")
    assert (ev.permanencia_seg,ev.motivo_cierre)==(3,"TRACK_LOST")
    with pytest.raises(ValueError):close_at_last_seen(ev,a,reason="OBSERVED_EXIT")


def test_processing_runs_keep_reused_tracker_ids_separate():
    engine=create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        shop=Tienda(nombre="Prueba",ubicacion="Local")
        db.add(shop);db.flush()
        cam=Camara(id_tienda=shop.id_tienda,nombre="Cam",fuente="sample.mp4")
        db.add(cam);db.flush()
        r1=Procesamiento(id_camara=cam.id_camara)
        r2=Procesamiento(id_camara=cam.id_camara)
        db.add_all([r1,r2]);db.flush()
        db.add_all([Track(id_camara=cam.id_camara,id_procesamiento=r1.id_procesamiento,external_track_id=1),Track(id_camara=cam.id_camara,id_procesamiento=r2.id_procesamiento,external_track_id=1)])
        db.commit()
        tracks=db.scalars(select(Track).order_by(Track.id_track)).all()
        assert tracks[0].external_track_id==tracks[1].external_track_id==1
        assert tracks[0].id_procesamiento!=tracks[1].id_procesamiento
