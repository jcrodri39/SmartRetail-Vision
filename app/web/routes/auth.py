import logging
from fastapi import APIRouter,Request,Form,Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.entities import Usuario
from app.core.security import verify_password,token
from app.core.config import settings
router=APIRouter()
log=logging.getLogger("smartretail.auth")
@router.get("/login")
def login_page(request:Request):return request.app.state.templates.TemplateResponse(request,"login.html",{"error":None})
@router.post("/login")
def login(request:Request,email:str=Form(...),password:str=Form(...),db:Session=Depends(get_db)):
    u=db.query(Usuario).filter(Usuario.email==email).first()
    if not u or not u.estado or not verify_password(password,u.password_hash):
        log.warning("Inicio de sesión rechazado para %s (%s)",email,"usuario inactivo" if u and not u.estado else "credenciales inválidas")
        return request.app.state.templates.TemplateResponse(request,"login.html",{"error":"Correo o contraseña incorrectos."},status_code=401)
    log.info("Inicio de sesión correcto: %s (rol %s)",email,u.rol)
    r=RedirectResponse("/dashboard",303);r.set_cookie("sv_session",token(u.id_usuario,u.rol),httponly=True,samesite="lax",secure=settings.session_cookie_secure,max_age=28800);return r
@router.get("/logout")
def logout():
    r=RedirectResponse("/login",303);r.delete_cookie("sv_session");return r
