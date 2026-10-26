from fastapi import HTTPException
from app.models.entities import Procesamiento, Camara

def validate_processing_scope(db, store_id, processing_id):
    """Validate session exists and belongs to requested store."""
    if processing_id is None:
        return
    p = db.get(Procesamiento, processing_id)
    if p is None:
        raise HTTPException(404, "Sesión de procesamiento no encontrada")
    cam = db.get(Camara, p.id_camara)
    if cam is None or (store_id is not None and cam.id_tienda != store_id):
        raise HTTPException(422, "La sesión no corresponde a la tienda seleccionada")
