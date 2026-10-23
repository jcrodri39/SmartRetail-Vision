from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.entities import Camara,Track,Deteccion,EventoZona,Zona
def dashboard(db:Session,store_id:int|None=None):
    qz=db.query(Zona)
    if store_id:qz=qz.filter(Zona.id_tienda==store_id)
    zones=qz.all(); rows=[]; total=0; dw=[]
    for z in zones:
        ev=db.query(EventoZona).filter(EventoZona.id_zona==z.id_zona).all()
        vals=[e.permanencia_seg for e in ev if e.permanencia_seg];dw+=vals;total+=len(ev)
        rows.append({"id":z.id_zona,"zona":z.nombre,"flujo":len(ev),"permanencia":round(sum(vals)/len(vals),1) if vals else 0,
                     "ocupacion":sum(1 for e in ev if e.salida is None)})
    tracks=db.query(Track).count();dets=db.query(Deteccion).count()
    return {"flujo":total,"permanencia":round(sum(dw)/len(dw),1) if dw else 0,"ocupacion":sum(r["ocupacion"] for r in rows),
            "tracks":tracks,"detecciones":dets,"zonas":rows}
