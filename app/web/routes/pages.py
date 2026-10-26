import json,logging,os,uuid
from pathlib import Path
from fastapi import APIRouter,Request,Depends,Form,UploadFile,File,HTTPException
from fastapi.responses import RedirectResponse,StreamingResponse,Response
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.deps import require
from app.models.entities import *
from app.core.security import hash_password
from app.analytics.zones import valid_polygon
from app.services.metrics import dashboard
from app.services.session_scope import validate_processing_scope
from app.services.reports import report_data,make_csv
from app.services.excel_report import make_xlsx,MIME_XLSX
from app.vision.live import live

router=APIRouter()
log=logging.getLogger("smartretail.web")
def sessions_for_store(db, sid):
    if sid is None: return []
    return (db.query(Procesamiento).join(Camara, Procesamiento.id_camara == Camara.id_camara)
            .filter(Camara.id_tienda == sid).order_by(Procesamiento.id_procesamiento.desc()).all())

def ctx(request,db,roles=None):
    u=require(request,db,roles);return u
@router.get("/")
def root():return RedirectResponse("/dashboard")
@router.get("/dashboard")
def dash(request:Request,store_id:int|None=None,processing_id:int|None=None,db:Session=Depends(get_db)):
    u=ctx(request,db);stores=db.query(Tienda).all();sid=store_id if store_id is not None else (stores[0].id_tienda if stores else None);validate_processing_scope(db,sid,processing_id)
    return request.app.state.templates.TemplateResponse(request,"dashboard.html",{"user":u,"stores":stores,"store_id":sid,"data":dashboard(db,sid,processing_id),"sessions":sessions_for_store(db,sid),"processing_id":processing_id})
@router.get("/videos")
def videos(request:Request,db:Session=Depends(get_db)):
    u=ctx(request,db,["ADMIN"]);return request.app.state.templates.TemplateResponse(request,"videos.html",{"user":u,"cameras":db.query(Camara).all(),"stores":db.query(Tienda).all()})
@router.post("/videos")
def video_add(request:Request,id_tienda:int=Form(...),nombre:str=Form(...),fuente:str=Form(...),db:Session=Depends(get_db)):
    u=ctx(request,db,["ADMIN"]);
    if db.get(Tienda,id_tienda) is None: raise HTTPException(404,"Tienda no encontrada")
    db.add(Camara(id_tienda=id_tienda,nombre=nombre,fuente=fuente));db.commit()
    log.info("Fuente de video registrada por %s: '%s' -> %s",u.email,nombre,fuente)  # credenciales RTSP enmascaradas por el filtro
    return RedirectResponse("/videos",303)
@router.post("/videos/upload")
async def video_upload(request:Request,id_tienda:int=Form(...),nombre:str=Form(...),video:UploadFile=File(...),db:Session=Depends(get_db)):
    ctx(request,db,["ADMIN"]);
    if db.get(Tienda,id_tienda) is None: raise HTTPException(404,"Tienda no encontrada")
    ext=(video.filename or "").lower().rsplit(".",1)[-1]
    if ext not in {"mp4","avi","mov","mkv"}:
        log.warning("Carga de video rechazada: extensión '%s' no permitida",ext);raise HTTPException(400,"Formato de video no permitido")
    upload_dir=Path("app/uploads")
    upload_dir.mkdir(parents=True,exist_ok=True)
    path=upload_dir / f"{uuid.uuid4().hex}.{ext}"
    max_bytes=100 * 1024 * 1024
    total=0
    try:
        with path.open("wb") as output:
            while chunk := await video.read(1024 * 1024):
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(413,"El video supera el límite de 100 MiB")
                output.write(chunk)
        if total == 0:
            raise HTTPException(400,"El archivo está vacío")
    except Exception:
        path.unlink(missing_ok=True)
        raise
    path=str(path)
    db.add(Camara(id_tienda=id_tienda,nombre=nombre,fuente=path));db.commit();log.info("Video cargado: '%s' -> %s",nombre,path)
    return RedirectResponse("/videos",303)
@router.post("/videos/{cid}/toggle")
def video_toggle(cid:int,request:Request,db:Session=Depends(get_db)):
    ctx(request,db,["ADMIN"]);c=db.get(Camara,cid)
    if c is None:raise HTTPException(404,"Cámara no encontrada")
    c.estado=not c.estado;db.commit();return RedirectResponse("/videos",303)
@router.get("/zones")
def zones(request:Request,db:Session=Depends(get_db)):
    u=ctx(request,db,["ADMIN"]);return request.app.state.templates.TemplateResponse(request,"zones.html",{"user":u,"zones":db.query(Zona).all(),"stores":db.query(Tienda).all(),"cameras":db.query(Camara).all()})
@router.post("/zones")
def zone_add(request:Request,id_tienda:int=Form(...),nombre:str=Form(...),coordenadas_json:str=Form(...),db:Session=Depends(get_db)):
    ctx(request,db,["ADMIN"])
    if db.get(Tienda,id_tienda) is None: raise HTTPException(404,"Tienda no encontrada")
    if not valid_polygon(coordenadas_json):
        log.warning("Zona '%s' rechazada: polígono inválido",nombre);raise HTTPException(422,"Polígono inválido")
    db.add(Zona(id_tienda=id_tienda,nombre=nombre,coordenadas_json=coordenadas_json));db.commit()
    log.info("Zona '%s' creada en tienda %s",nombre,id_tienda);return RedirectResponse("/zones",303)
@router.post("/zones/{zid}/toggle")
def zone_toggle(zid:int,request:Request,db:Session=Depends(get_db)):
    ctx(request,db,["ADMIN"]);z=db.get(Zona,zid)
    if z is None:raise HTTPException(404,"Zona no encontrada")
    z.estado=not z.estado;db.commit();return RedirectResponse("/zones",303)
@router.post("/zones/{zid}/delete")
def zone_delete(zid:int,request:Request,db:Session=Depends(get_db)):
    ctx(request,db,["ADMIN"]);z=db.get(Zona,zid)
    if z is None:raise HTTPException(404,"Zona no encontrada")
    db.delete(z);db.commit();log.info("Zona %s eliminada",zid);return RedirectResponse("/zones",303)
@router.get("/vision")
def vision(request:Request,db:Session=Depends(get_db)):
    u=ctx(request,db);return request.app.state.templates.TemplateResponse(request,"vision.html",{"user":u,"cameras":db.query(Camara).filter(Camara.estado==True).all()})
@router.post("/vision/start/{cid}")
def vision_start(cid:int,request:Request,db:Session=Depends(get_db)):
    u=ctx(request,db);log.info("YOLO Live solicitado por %s para la cámara %s",u.email,cid);
    if not live.start(cid):
        raise HTTPException(409,"Ya existe un procesamiento activo o en proceso de cierre")
    return {"ok":True}
@router.post("/vision/stop")
def vision_stop(request:Request,db:Session=Depends(get_db)):
    u=ctx(request,db);log.info("YOLO Live detenido por %s",u.email);live.stop();return {"ok":True}
@router.get("/vision/stream")
def vision_stream(request:Request,db:Session=Depends(get_db)):
    ctx(request,db)
    import time
    def gen():
        while True:
            if live.latest:yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"+live.latest+b"\r\n"
            time.sleep(.04)
    return StreamingResponse(gen(),media_type="multipart/x-mixed-replace; boundary=frame")
@router.get("/vision/status")
def vision_status(request:Request,db:Session=Depends(get_db)):ctx(request,db);return {"running":live.running,**live.stats,"events":list(live.events)}
@router.get("/heatmap")
def heatmap(request:Request,store_id:int|None=None,processing_id:int|None=None,db:Session=Depends(get_db)):
    u=ctx(request,db);stores=db.query(Tienda).all();sid=store_id if store_id is not None else (stores[0].id_tienda if stores else None);validate_processing_scope(db,sid,processing_id);points=[]
    if sid:
        query=db.query(Deteccion.cx,Deteccion.cy).join(Track,Track.id_track==Deteccion.id_track).join(Camara,Camara.id_camara==Track.id_camara).filter(Camara.id_tienda==sid)
        if processing_id is not None: query=query.filter(Track.id_procesamiento==processing_id)
        points=query.order_by(Deteccion.id_deteccion.desc()).limit(4000).all()
    return request.app.state.templates.TemplateResponse(request,"heatmap.html",{"user":u,"stores":stores,"store_id":sid,"points":[list(p) for p in points],"sessions":sessions_for_store(db,sid),"processing_id":processing_id})
@router.get("/reports")
def reports(request:Request,store_id:int|None=None,processing_id:int|None=None,db:Session=Depends(get_db)):
    u=ctx(request,db);stores=db.query(Tienda).all();sid=store_id if store_id is not None else (stores[0].id_tienda if stores else None)
    validate_processing_scope(db,sid,processing_id)
    return request.app.state.templates.TemplateResponse(request,"reports.html",{"user":u,"stores":stores,"store_id":sid,"processing_id":processing_id,"sessions":sessions_for_store(db,sid),"data":report_data(db,sid,processing_id),"reports":db.query(Reporte).order_by(Reporte.id_reporte.desc()).limit(20).all()})
@router.get("/reports/data")
def reports_data(request:Request,store_id:int|None=None,processing_id:int|None=None,db:Session=Depends(get_db)):
    ctx(request,db);validate_processing_scope(db,store_id,processing_id);return report_data(db,store_id,processing_id)
@router.get("/reports/download")
def report_download(request:Request,store_id:int|None=None,processing_id:int|None=None,db:Session=Depends(get_db)):
    u=ctx(request,db);validate_processing_scope(db,store_id,processing_id);csv,rep=make_csv(db,u.id_usuario,store_id,processing_id);log.info("Reporte CSV #%s generado por %s",rep.id_reporte,u.email)
    return Response(csv,media_type="text/csv",headers={"Content-Disposition":"attachment; filename=smartretail_report.csv"})
@router.get("/reports/download.xlsx")
def report_download_xlsx(request:Request,store_id:int|None=None,processing_id:int|None=None,db:Session=Depends(get_db)):
    # UC007: exportación Excel (equivalente Apache POI -> openpyxl)
    u=ctx(request,db)
    validate_processing_scope(db,store_id,processing_id)
    try:contenido,rep=make_xlsx(db,u,store_id,processing_id)
    except Exception:
        log.exception("Error al generar el reporte Excel (tienda %s)",store_id);raise HTTPException(500,"No fue posible generar el reporte Excel")
    nombre=f"smartretail_reporte_{rep.id_reporte}.xlsx"
    return Response(contenido,media_type=MIME_XLSX,headers={"Content-Disposition":f"attachment; filename={nombre}"})
@router.get("/users")
def users(request:Request,db:Session=Depends(get_db)):
    u=ctx(request,db,["ADMIN"]);return request.app.state.templates.TemplateResponse(request,"users.html",{"user":u,"users":db.query(Usuario).all()})
@router.post("/users")
def user_add(request:Request,nombre:str=Form(...),email:str=Form(...),password:str=Form(...),rol:str=Form(...),db:Session=Depends(get_db)):
    me=ctx(request,db,["ADMIN"]);
    if rol not in {"ADMIN","ANALYST"}: raise HTTPException(422,"Rol no válido")
    if len(password) < 12: raise HTTPException(422,"La contraseña debe tener al menos 12 caracteres")
    if db.query(Usuario).filter(Usuario.email==email).first(): raise HTTPException(409,"El correo ya está registrado")
    db.add(Usuario(nombre=nombre,email=email,password_hash=hash_password(password),rol=rol));db.commit()
    log.info("Usuario %s creado con rol %s por %s",email,rol,me.email);return RedirectResponse("/users",303)
@router.post("/users/{uid}/toggle")
def user_toggle(uid:int,request:Request,db:Session=Depends(get_db)):
    me=ctx(request,db,["ADMIN"]);u=db.get(Usuario,uid)
    if u is None:raise HTTPException(404,"Usuario no encontrado")
    if u.id_usuario!=me.id_usuario:u.estado=not u.estado;db.commit();log.info("Usuario %s %s",u.email,"activado" if u.estado else "desactivado")
    return RedirectResponse("/users",303)
@router.post("/users/{uid}/role")
def user_role(uid:int,request:Request,rol:str=Form(...),db:Session=Depends(get_db)):
    ctx(request,db,["ADMIN"]);u=db.get(Usuario,uid)
    if u is None:raise HTTPException(404,"Usuario no encontrado")
    if rol not in {"ADMIN","ANALYST"}:raise HTTPException(422,"Rol no válido")
    u.rol=rol;db.commit();log.info("Rol de %s cambiado a %s",u.email,rol)
    return RedirectResponse("/users",303)
