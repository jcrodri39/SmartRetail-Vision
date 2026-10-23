import csv, io, json
from datetime import datetime
from sqlalchemy import func
from app.models.entities import Reporte, Zona, EventoZona, Deteccion, Track, Camara
from app.services.metrics import dashboard

def report_data(db, store_id=None):
    data=dashboard(db,store_id)
    camera_ids=[]
    if store_id:
        camera_ids=[x[0] for x in db.query(Camara.id_camara).filter(Camara.id_tienda==store_id).all()]
    tq=db.query(Track)
    if camera_ids:tq=tq.filter(Track.id_camara.in_(camera_ids))
    track_ids=[x[0] for x in tq.with_entities(Track.id_track).all()]
    dq=db.query(Deteccion)
    if track_ids:dq=dq.filter(Deteccion.id_track.in_(track_ids))
    elif store_id:dq=dq.filter(False)
    conf=dq.with_entities(func.avg(Deteccion.confidence)).scalar() or 0
    events=[]
    if data["zonas"]:
        zone_ids=[z["id"] for z in data["zonas"]]
        events=db.query(EventoZona).filter(EventoZona.id_zona.in_(zone_ids)).all()
    dwell=[e.permanencia_seg for e in events if e.permanencia_seg and e.permanencia_seg>0]
    completed=[e for e in events if e.salida is not None]
    top_flow=max(data["zonas"],key=lambda z:z["flujo"],default=None)
    top_dwell=max(data["zonas"],key=lambda z:z["permanencia"],default=None)
    data["advanced"]={
        "confidence_avg":round(float(conf)*100,1),
        "completed_visits":len(completed),
        "dwell_max":round(max(dwell),1) if dwell else 0,
        "zones_count":len(data["zonas"]),
        "top_flow":top_flow["zona"] if top_flow else "Sin datos",
        "top_flow_value":top_flow["flujo"] if top_flow else 0,
        "top_dwell":top_dwell["zona"] if top_dwell else "Sin datos",
        "top_dwell_value":top_dwell["permanencia"] if top_dwell else 0,
    }
    return data

def make_csv(db,user_id,store_id=None):
    data=report_data(db,store_id);s=io.StringIO();w=csv.writer(s)
    w.writerow(["SMARTRETAIL VISION","REPORTE EJECUTIVO DE ANALITICA"])
    w.writerow(["Generado",datetime.now().isoformat(timespec="seconds")])
    w.writerow([])
    w.writerow(["KPI","Valor"])
    for k,v in [
        ("Flujo total",data["flujo"]),("Permanencia promedio (s)",data["permanencia"]),
        ("Ocupacion actual",data["ocupacion"]),("Tracks",data["tracks"]),
        ("Detecciones YOLO",data["detecciones"]),("Confianza YOLO promedio (%)",data["advanced"]["confidence_avg"]),
        ("Visitas completadas",data["advanced"]["completed_visits"]),("Permanencia maxima (s)",data["advanced"]["dwell_max"]),
        ("Zona mayor flujo",data["advanced"]["top_flow"]),("Zona mayor permanencia",data["advanced"]["top_dwell"])
    ]: w.writerow([k,v])
    w.writerow([]);w.writerow(["Zona","Flujo","Permanencia promedio (s)","Ocupacion"])
    for r in data["zonas"]:w.writerow([r["zona"],r["flujo"],r["permanencia"],r["ocupacion"]])
    rep=Reporte(id_usuario=user_id,tipo="CSV_ANALYTICS",parametros=json.dumps({"store_id":store_id}))
    db.add(rep);db.commit();db.refresh(rep)
    return s.getvalue(),rep
