from datetime import datetime
from sqlalchemy import String,Text,Float,Boolean,DateTime,ForeignKey,Integer
from sqlalchemy.orm import Mapped,mapped_column
from app.db.database import Base
class Usuario(Base):
    __tablename__="usuario";id_usuario:Mapped[int]=mapped_column(primary_key=True)
    nombre:Mapped[str]=mapped_column(String(120));email:Mapped[str]=mapped_column(String(180),unique=True,index=True)
    password_hash:Mapped[str]=mapped_column(String(255));rol:Mapped[str]=mapped_column(String(20));estado:Mapped[bool]=mapped_column(Boolean,default=True)
class Tienda(Base):
    __tablename__="tienda";id_tienda:Mapped[int]=mapped_column(primary_key=True);nombre:Mapped[str]=mapped_column(String(120));ubicacion:Mapped[str]=mapped_column(String(180),default="")
class Camara(Base):
    __tablename__="camara";id_camara:Mapped[int]=mapped_column(primary_key=True);id_tienda:Mapped[int]=mapped_column(ForeignKey("tienda.id_tienda"),index=True)
    nombre:Mapped[str]=mapped_column(String(120));fuente:Mapped[str]=mapped_column(Text);estado:Mapped[bool]=mapped_column(Boolean,default=True)
class Zona(Base):
    __tablename__="zona";id_zona:Mapped[int]=mapped_column(primary_key=True);id_tienda:Mapped[int]=mapped_column(ForeignKey("tienda.id_tienda"),index=True)
    nombre:Mapped[str]=mapped_column(String(120));coordenadas_json:Mapped[str]=mapped_column(Text);estado:Mapped[bool]=mapped_column(Boolean,default=True)
class Procesamiento(Base):
    """Ejecución independiente de una fuente de video."""
    __tablename__ = "procesamiento"
    id_procesamiento: Mapped[int] = mapped_column(primary_key=True)
    id_camara: Mapped[int] = mapped_column(ForeignKey("camara.id_camara"), index=True)
    inicio: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fin: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="RUNNING")

class Track(Base):
    __tablename__="track";id_track:Mapped[int]=mapped_column(primary_key=True);id_camara:Mapped[int]=mapped_column(ForeignKey("camara.id_camara"),index=True)
    external_track_id:Mapped[int]=mapped_column(Integer,index=True);id_procesamiento:Mapped[int|None]=mapped_column(ForeignKey("procesamiento.id_procesamiento"),nullable=True,index=True);inicio:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,index=True);fin:Mapped[datetime|None]=mapped_column(DateTime,nullable=True)
class Deteccion(Base):
    __tablename__="deteccion";id_deteccion:Mapped[int]=mapped_column(primary_key=True);id_track:Mapped[int]=mapped_column(ForeignKey("track.id_track"),index=True)
    timestamp:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,index=True);x1:Mapped[float]=mapped_column(Float);y1:Mapped[float]=mapped_column(Float)
    x2:Mapped[float]=mapped_column(Float);y2:Mapped[float]=mapped_column(Float);cx:Mapped[float]=mapped_column(Float);cy:Mapped[float]=mapped_column(Float);confidence:Mapped[float]=mapped_column(Float)
class EventoZona(Base):
    __tablename__="evento_zona";id_evento:Mapped[int]=mapped_column(primary_key=True);id_track:Mapped[int]=mapped_column(ForeignKey("track.id_track"),index=True)
    id_zona:Mapped[int]=mapped_column(ForeignKey("zona.id_zona"),index=True);tipo:Mapped[str]=mapped_column(String(20),default="ENTRY")
    entrada:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,index=True);salida:Mapped[datetime|None]=mapped_column(DateTime,nullable=True);permanencia_seg:Mapped[float]=mapped_column(Float,default=0)
    motivo_cierre:Mapped[str|None]=mapped_column(String(24),nullable=True)
class Metrica(Base):
    __tablename__="metrica";id_metrica:Mapped[int]=mapped_column(primary_key=True);id_zona:Mapped[int]=mapped_column(ForeignKey("zona.id_zona"),index=True)
    tipo:Mapped[str]=mapped_column(String(50));valor:Mapped[float]=mapped_column(Float);periodo_inicio:Mapped[datetime]=mapped_column(DateTime,index=True);periodo_fin:Mapped[datetime]=mapped_column(DateTime,index=True)
class Reporte(Base):
    __tablename__="reporte";id_reporte:Mapped[int]=mapped_column(primary_key=True);id_usuario:Mapped[int]=mapped_column(ForeignKey("usuario.id_usuario"),index=True)
    tipo:Mapped[str]=mapped_column(String(30));fecha_generacion:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow);parametros:Mapped[str]=mapped_column(Text,default="{}")
