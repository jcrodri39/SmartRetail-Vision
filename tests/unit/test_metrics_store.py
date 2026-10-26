from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.database import Base
from app.models.entities import Tienda, Camara, Zona, Track, Deteccion, EventoZona
from app.services.metrics import dashboard
from app.services.reports import report_data


def test_store_isolation_and_event_semantics():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add_all([Tienda(id_tienda=1, nombre="A"), Tienda(id_tienda=2, nombre="B")]); db.flush()
        db.add_all([Camara(id_camara=1,id_tienda=1,nombre="A",fuente="a"),
                    Camara(id_camara=2,id_tienda=2,nombre="B",fuente="b")]); db.flush()
        db.add_all([Zona(id_zona=1,id_tienda=1,nombre="Z1",coordenadas_json="[]"),
                    Zona(id_zona=2,id_tienda=2,nombre="Z2",coordenadas_json="[]")]); db.flush()
        db.add_all([Track(id_track=1,id_camara=1,external_track_id=1),
                    Track(id_track=2,id_camara=2,external_track_id=1)]); db.flush()
        t=datetime(2026,1,1)
        db.add_all([Deteccion(id_track=1,timestamp=t,x1=0,y1=0,x2=1,y2=1,cx=.5,cy=1,confidence=.8),
                    Deteccion(id_track=2,timestamp=t,x1=0,y1=0,x2=1,y2=1,cx=.5,cy=1,confidence=.4)])
        db.add_all([EventoZona(id_track=1,id_zona=1,tipo="ENTRY",entrada=t,salida=t+timedelta(seconds=0),permanencia_seg=0),
                    EventoZona(id_track=2,id_zona=2,tipo="ENTRY",entrada=t,salida=None,permanencia_seg=0)])
        db.commit()
        a,b=dashboard(db,1),dashboard(db,2)
        assert (a["tracks"],a["detecciones"],a["flujo"],a["ocupacion"],a["permanencia"]) == (1,1,1,0,0)
        assert (b["tracks"],b["detecciones"],b["flujo"],b["ocupacion"]) == (1,1,1,1)
        assert dashboard(db,999)["tracks"] == 0
        assert report_data(db,1)["advanced"]["confidence_avg"] == 80.0
        assert report_data(db,2)["advanced"]["confidence_avg"] == 40.0
        assert dashboard(db,None)["tracks"] == 2
