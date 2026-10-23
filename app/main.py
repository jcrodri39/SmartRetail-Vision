import logging
from fastapi import FastAPI,Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.core.config import settings
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
        db.add_all([Usuario(nombre="Administrador",email="admin@smartretail.local",password_hash=hash_password("Admin123*"),rol="ADMIN"),
                    Usuario(nombre="Analista",email="analyst@smartretail.local",password_hash=hash_password("Analyst123*"),rol="ANALYST")])
        log.info("Usuarios iniciales creados (ADMIN y ANALYST)")
    if not db.query(Tienda).first():db.add(Tienda(nombre="Tienda Demo",ubicacion="Demo"))
    db.commit();db.close()
seed()
app=FastAPI(title="SmartRetail Vision",version="5.0")
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
