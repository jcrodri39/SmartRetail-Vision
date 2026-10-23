from fastapi import Request,HTTPException
from sqlalchemy.orm import Session
from app.core.security import decode
from app.models.entities import Usuario
def current_user(request:Request,db:Session):
    raw=request.cookies.get("sv_session")
    if not raw:return None
    try:
        p=decode(raw);u=db.get(Usuario,int(p["sub"]))
        return u if u and u.estado else None
    except Exception:return None
def require(request,db,roles=None):
    u=current_user(request,db)
    if not u:raise HTTPException(401,"Sesión requerida")
    if roles and u.rol not in roles:raise HTTPException(403,"No autorizado")
    return u
