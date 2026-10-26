"""Smoke tests: real HTTP + SQLite data; no neural network required."""
from uuid import uuid4
from io import BytesIO
from zipfile import ZipFile
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.entities import Usuario,Tienda,Camara,Procesamiento,Track,Deteccion,Zona,EventoZona
from app.core.security import hash_password

ORIGIN={"Origin":"http://testserver"}

def test_minimum_authenticated_reports_and_exports():
    db=SessionLocal()
    tag=uuid4().hex
    user=Usuario(nombre='Smoke',email=f'smoke-{tag}@example.test',password_hash=hash_password('TestPassword-2026!'),rol='ADMIN')
    store=Tienda(nombre=f'Smoke store {tag}',ubicacion='Test')
    db.add_all([user,store]);db.flush()
    camera=Camara(id_tienda=store.id_tienda,nombre='Camera',fuente='test.mp4')
    zone=Zona(id_tienda=store.id_tienda,nombre='Entrance',coordenadas_json='[[0,0],[100,0],[100,100],[0,100]]')
    db.add_all([camera,zone]);db.flush()
    processing=Procesamiento(id_camara=camera.id_camara,estado='FINISHED')
    db.add(processing);db.flush()
    track=Track(id_camara=camera.id_camara,id_procesamiento=processing.id_procesamiento,external_track_id=1)
    db.add(track);db.flush()
    db.add(Deteccion(id_track=track.id_track,x1=0,y1=0,x2=20,y2=30,cx=10,cy=15,confidence=.85))
    db.add(EventoZona(id_track=track.id_track,id_zona=zone.id_zona,permanencia_seg=12,motivo_cierre='OBSERVED_EXIT'))
    db.commit()
    try:
        with TestClient(app,base_url='http://testserver') as client:
            login=client.post('/login',data={'email':user.email,'password':'TestPassword-2026!'},headers=ORIGIN,follow_redirects=False)
            assert login.status_code==303,login.text
            params={'store_id':store.id_tienda,'processing_id':processing.id_procesamiento}
            for route in ('/dashboard','/reports','/heatmap'):
                resp=client.get(route,params=params)
                assert resp.status_code==200,(route,resp.status_code,resp.text[:400])
            result=client.get('/reports/data',params=params)
            assert result.status_code==200,result.text
            data=result.json()
            assert data['tracks']==1,data
            assert data['detecciones']==1,data
            csv=client.get('/reports/download',params=params)
            assert csv.status_code==200,csv.text[:400]
            assert 'text/csv' in csv.headers['content-type']
            assert 'Entrance' in csv.text
            excel=client.get('/reports/download.xlsx',params=params)
            assert excel.status_code==200,excel.text[:400] if not excel.content.startswith(b'PK') else 'zip'
            with ZipFile(BytesIO(excel.content)) as archive:
                assert 'xl/workbook.xml' in archive.namelist()
            other=client.get('/reports/data',params={'store_id':store.id_tienda,'processing_id':processing.id_procesamiento+999999})
            assert other.status_code in (400,404),other.text
    finally:
        db.rollback()
        from app.models.entities import Reporte
        db.query(Reporte).filter(Reporte.id_usuario==user.id_usuario).delete()
        db.query(EventoZona).filter(EventoZona.id_track==track.id_track).delete()
        db.query(Deteccion).filter(Deteccion.id_track==track.id_track).delete()
        db.delete(track);db.delete(processing);db.delete(zone);db.delete(camera);db.delete(store);db.delete(user)
        db.commit();db.close()
