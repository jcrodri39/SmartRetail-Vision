import cv2,threading,time,json,logging
from collections import deque
from datetime import datetime
from app.core.config import settings
from app.core.logging_config import sesion_log,RegistroRendimiento
from app.db.database import SessionLocal
from app.models.entities import Camara,Zona,Track,Deteccion,EventoZona
from app.analytics.zones import inside
log=logging.getLogger("smartretail.vision")
class LiveVision:
    def __init__(self):
        self.running=False;self.latest=None;self.camera_id=None;self.events=deque(maxlen=40);self.lock=threading.Lock()
        self.stats={"fps":0,"latency":0,"persons":0,"tracks":0,"frames":0,"entries":0,"exits":0}
    def start(self,camera_id):
        if self.running:self.stop();time.sleep(.2)
        self.camera_id=camera_id;self.running=True;threading.Thread(target=self._work,daemon=True).start()
    def stop(self):self.running=False
    def _work(self):
        # Id de sesión de procesamiento: acompaña cada línea de log de esta ejecución (MDC de LogBack)
        with sesion_log(f"cam{self.camera_id}-{datetime.utcnow():%Y%m%dT%H%M%S}"):
            self._procesar()
    def _procesar(self):
        from ultralytics import YOLO
        db=SessionLocal();cam=db.get(Camara,self.camera_id)
        if not cam:
            log.error("Cámara %s no existe; no se inicia el procesamiento",self.camera_id)
            self.running=False;db.close();return
        source=int(cam.fuente) if str(cam.fuente).isdigit() else cam.fuente
        cap=cv2.VideoCapture(source)
        if not cap.isOpened():   # UC004 flujo alternativo 1A: fuente no disponible
            log.error("No se pudo abrir la fuente de la cámara %s (%s)",cam.id_camara,cam.fuente)
            self.running=False;db.close();return
        model=YOLO(settings.yolo_model);track_rows={};active={};trail={}
        zones=db.query(Zona).filter(Zona.id_tienda==cam.id_tienda,Zona.estado==True).all();last=time.perf_counter()
        log.info("Procesamiento iniciado: cámara %s '%s' | %d zonas activas | modelo=%s conf=%.2f iou=%.2f tracker=%s",
                 cam.id_camara,cam.nombre,len(zones),settings.yolo_model,settings.yolo_confidence,settings.yolo_iou,settings.yolo_tracker)
        if not zones:log.warning("La tienda %s no tiene zonas activas: no se generarán eventos de zona",cam.id_tienda)
        perf=RegistroRendimiento(cada_n_frames=100)   # RNF001: FPS y latencia en logs/rendimiento.csv
        motivo="detenido por el usuario"
        try:
            while self.running and cap.isOpened():
                ok,frame=cap.read()
                if not ok:   # fin del archivo o la fuente dejó de entregar cuadros
                    motivo="fin de la fuente o lectura fallida";break
                t=time.perf_counter();device=None if settings.yolo_device=="auto" else settings.yolo_device
                with perf.medir("yolo_tracking"):
                    rs=model.track(frame,persist=True,classes=[0],conf=settings.yolo_confidence,iou=settings.yolo_iou,
                        imgsz=settings.yolo_image_size,tracker=settings.yolo_tracker,device=device,verbose=False)
                latency=(time.perf_counter()-t)*1000;dets=[]
                if rs and rs[0].boxes is not None and rs[0].boxes.id is not None:
                    for box,conf,tid in zip(rs[0].boxes.xyxy.cpu().tolist(),rs[0].boxes.conf.cpu().tolist(),rs[0].boxes.id.int().cpu().tolist()):
                        dets.append((list(map(float,box)),float(conf),int(tid)))
                now=datetime.utcnow()
                with perf.medir("zonas_eventos_bd"):
                    for z in zones:
                        pts=json.loads(z.coordenadas_json);cv2.polylines(frame,[__import__("numpy").array(pts,dtype="int32")],True,(255,170,0),2)
                        cv2.putText(frame,z.nombre,tuple(map(int,pts[0])),cv2.FONT_HERSHEY_SIMPLEX,.6,(255,170,0),2)
                    for box,conf,tid in dets:
                        x1,y1,x2,y2=box;cx,cy=(x1+x2)/2,(y1+y2)/2
                        if tid not in track_rows:
                            tr=Track(id_camara=cam.id_camara,external_track_id=tid,inicio=now);db.add(tr);db.flush();track_rows[tid]=tr
                            log.debug("Nuevo track temporal %s",tid)
                        tr=track_rows[tid];db.add(Deteccion(id_track=tr.id_track,timestamp=now,x1=x1,y1=y1,x2=x2,y2=y2,cx=cx,cy=cy,confidence=conf))
                        trail.setdefault(tid,deque(maxlen=20)).append((int(cx),int(cy)))
                        pts=list(trail[tid])
                        for a,b in zip(pts,pts[1:]):cv2.line(frame,a,b,(0,220,255),2)
                        for z in zones:
                            key=(tid,z.id_zona);inn=inside(z.coordenadas_json,(cx,cy))
                            if inn and key not in active:
                                ev=EventoZona(id_track=tr.id_track,id_zona=z.id_zona,tipo="ENTRY",entrada=now);db.add(ev);db.flush();active[key]=ev
                                self.stats["entries"]+=1;self.events.appendleft(f"{now:%H:%M:%S} · ID {tid} · ENTRY · {z.nombre}")
                                log.debug("ENTRY track %s en zona '%s'",tid,z.nombre)
                            elif not inn and key in active:
                                ev=active.pop(key);ev.salida=now;ev.permanencia_seg=(now-ev.entrada).total_seconds();self.stats["exits"]+=1
                                self.events.appendleft(f"{now:%H:%M:%S} · ID {tid} · EXIT · {z.nombre}")
                                log.debug("EXIT track %s de zona '%s' tras %.1f s",tid,z.nombre,ev.permanencia_seg)
                        cv2.rectangle(frame,(int(x1),int(y1)),(int(x2),int(y2)),(30,230,100),2);cv2.circle(frame,(int(cx),int(cy)),4,(0,220,255),-1)
                        cv2.putText(frame,f"Person ID {tid} {conf:.0%}",(int(x1),max(20,int(y1)-7)),cv2.FONT_HERSHEY_SIMPLEX,.55,(30,230,100),2)
                    db.commit()
                nowp=time.perf_counter();fps=1/max(nowp-last,1e-6);last=nowp
                with perf.medir("codificacion_jpg"):
                    ok,jpg=cv2.imencode(".jpg",frame,[int(cv2.IMWRITE_JPEG_QUALITY),82])
                if ok:
                    with self.lock:self.latest=jpg.tobytes()
                else:log.warning("No se pudo codificar el frame %d para el monitor",self.stats["frames"]+1)
                self.stats.update(fps=round(fps,1),latency=round(latency,1),persons=len(dets),tracks=len(track_rows),frames=self.stats["frames"]+1)
                perf.frame_procesado(len(dets))
        except Exception:
            motivo="error";log.exception("Error en el pipeline de visión (frame %d)",self.stats["frames"])
        finally:
            perf.volcar()
            end=datetime.utcnow()
            for tr in track_rows.values():tr.fin=end
            for ev in active.values():ev.salida=end;ev.permanencia_seg=(end-ev.entrada).total_seconds()
            db.commit();db.close();cap.release();self.running=False
            log.info("Procesamiento finalizado (%s): %d frames | %d tracks | %d ENTRY | %d EXIT | %d presencias cerradas al terminar",
                     motivo,self.stats["frames"],len(track_rows),self.stats["entries"],self.stats["exits"],len(active))
live=LiveVision()
