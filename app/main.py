import logging
from fastapi import FastAPI,Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.core.config import settings
import os
from app.core.logging_config import configurar_logging,detener_logging
configurar_logging(settings.log_dir,settings.log_level)   # LogBack -> logging (antes de todo lo demás)
log=logging.getLogger("smartretail.app")
from app.db.database import Base,engine,SessionLocal
from app.models.entities import Usuario,Tienda
from app.core.security import hash_password
from app.web.routes.auth import router as auth
from app.web.routes.pages import router as pages
Base.metadata.create_all(engine)
def seed():
    db=SessionLocal()
    if not db.query(Usuario).first():
        if settings.bootstrap_admin_email and settings.bootstrap_admin_password:
            if len(settings.bootstrap_admin_password) < 12:
                raise ValueError("BOOTSTRAP_ADMIN_PASSWORD debe contener al menos 12 caracteres")
            db.add(Usuario(nombre="Administrador",email=settings.bootstrap_admin_email,password_hash=hash_password(settings.bootstrap_admin_password),rol="ADMIN"))
            log.info("Cuenta inicial de administrador creada desde variables de entorno")
        else:
            log.warning("Sin usuarios: defina BOOTSTRAP_ADMIN_EMAIL y BOOTSTRAP_ADMIN_PASSWORD para crear un administrador")
    if not db.query(Tienda).first():db.add(Tienda(nombre="Tienda Demo",ubicacion="Demo"))
    db.commit();db.close()
seed()
app=FastAPI(title="SmartRetail Vision",version="5.0")
from fastapi.responses import JSONResponse
from app.core.request_origin import same_origin_request

@app.middleware("http")
async def protect_browser_writes(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        expected = os.getenv("SMARTRETAIL_PUBLIC_ORIGIN") or str(request.base_url).rstrip("/")
        if not same_origin_request(expected, request.headers.get("origin"), request.headers.get("referer")):
            return JSONResponse({"detail": "Origen de solicitud no autorizado"}, status_code=403)
    return await call_next(request)

app.state.templates=Jinja2Templates(directory="app/web/templates")
app.mount("/static",StaticFiles(directory="app/web/static"),name="static")
app.include_router(auth);app.include_router(pages)
log.info("SmartRetail Vision 5.0 iniciado | BD=%s | modelo=%s | tracker=%s",
         settings.database_url.split(":",1)[0],settings.yolo_model,settings.yolo_tracker)
@app.on_event("shutdown")
def _cerrar_bitacora():
    log.info("Aplicación detenida");detener_logging()
@app.get("/health")
def health():return {"status":"ok"}
