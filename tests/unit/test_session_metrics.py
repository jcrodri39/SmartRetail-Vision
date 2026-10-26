from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.database import Base
from app.models.entities import Tienda, Camara, Zona, Procesamiento, Track, Deteccion, EventoZona
from app.services.metrics import dashboard
from app.services.reports import report_data
from app.services.session_scope import validate_processing_scope


def test_session_filter_prevents_reprocessing_double_count():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add_all([Tienda(id_tienda=1,nombre='A'),Tienda(id_tienda=2,nombre='B')]);db.flush()
        db.add_all([Camara(id_camara=1,id_tienda=1,nombre='C1',fuente='file'),Camara(id_camara=2,id_tienda=2,nombre='C2',fuente='file')]);db.flush()
        db.add_all([Zona(id_zona=1,id_tienda=1,nombre='Z1',coordenadas_json='[]'),Zona(id_zona=2,id_tienda=2,nombre='Z2',coordenadas_json='[]')]);db.flush()
        db.add_all([Procesamiento(id_procesamiento=1,id_camara=1),Procesamiento(id_procesamiento=2,id_camara=1),Procesamiento(id_procesamiento=3,id_camara=2)]);db.flush()
        for n,cam,proc,zone in [(1,1,1,1),(2,1,2,1),(3,2,3,2)]:
            db.add(Track(id_track=n,id_camara=cam,id_procesamiento=proc,external_track_id=1))
        db.flush()
        t=datetime(2026,1,1)
        for n,zone in [(1,1),(2,1),(3,2)]:
            db.add(Deteccion(id_track=n,timestamp=t,x1=0,y1=0,x2=2,y2=2,cx=1,cy=2,confidence=.7))
            db.add(EventoZona(id_track=n,id_zona=zone,tipo='ENTRY',entrada=t,salida=t+timedelta(seconds=n),permanencia_seg=n))
        db.commit()
        assert dashboard(db,1)['flujo']==2
        assert dashboard(db,1,1)['flujo']==1
        assert dashboard(db,1,1)['tracks']==1
        assert dashboard(db,1,1)['detecciones']==1
        assert dashboard(db,1,2)['permanencia']==2
        assert dashboard(db,2,1)['flujo']==0
        assert report_data(db,1,1)['advanced']['completed_visits']==1
        validate_processing_scope(db,1,1)
        for store,proc,expected in [(1,3,422),(1,999,404)]:
            try:
                validate_processing_scope(db,store,proc)
                assert False,'Expected error'
            except HTTPException as exc:
                assert exc.status_code==expected
