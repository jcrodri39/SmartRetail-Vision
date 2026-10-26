"""Indicadores observacionales agregados, acotados por tienda.

Flujo significa eventos ENTRY por zona, NO visitantes únicos de la tienda.
Ocupación significa eventos abiertos, NO aforo físico validado.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.entities import Camara, Track, Deteccion, EventoZona, Zona, Procesamiento


def dashboard(db: Session, store_id: int | None = None, processing_id: int | None = None):
    """Calcula métricas; store_id=None agrega todas las tiendas explícitamente."""
    qz = db.query(Zona)
    qt = db.query(Track).join(Camara, Track.id_camara == Camara.id_camara)
    qd = db.query(Deteccion).join(Track, Deteccion.id_track == Track.id_track).join(
        Camara, Track.id_camara == Camara.id_camara
    )
    if store_id is not None:
        qz = qz.filter(Zona.id_tienda == store_id)
        qt = qt.filter(Camara.id_tienda == store_id)
        qd = qd.filter(Camara.id_tienda == store_id)
    if processing_id is not None:
        qt = qt.filter(Track.id_procesamiento == processing_id)
        qd = qd.filter(Track.id_procesamiento == processing_id)
    rows, dwell, total, occupancy = [], [], 0, 0
    for zone in qz.order_by(Zona.id_zona).all():
        eq = db.query(EventoZona).join(Track, EventoZona.id_track == Track.id_track).filter(EventoZona.id_zona == zone.id_zona)
        if processing_id is not None:
            eq = eq.filter(Track.id_procesamiento == processing_id)
        events = eq.all()
        # Un evento ENTRY representa una visita observada a una zona, no una persona única.
        entries = [e for e in events if e.tipo == "ENTRY"]
        durations = [e.permanencia_seg for e in entries
                     if e.salida is not None and e.permanencia_seg is not None and e.permanencia_seg >= 0]
        open_events = sum(1 for e in entries if e.salida is None)
        dwell.extend(durations)
        total += len(entries)
        occupancy += open_events
        rows.append({"id": zone.id_zona, "zona": zone.nombre, "flujo": len(entries),
                     "permanencia": round(sum(durations) / len(durations), 1) if durations else 0,
                     "ocupacion": open_events})
    return {"flujo": total, "permanencia": round(sum(dwell) / len(dwell), 1) if dwell else 0,
            "ocupacion": occupancy, "tracks": qt.count(), "detecciones": qd.count(),
            "zonas": rows}
