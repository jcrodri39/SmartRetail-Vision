# Arquitectura V4
Modular Monolith: Web Routes → Services/Analytics → Domain Models → SQLAlchemy; Vision Live separado en worker thread.
Cadena UC004: Cámara/archivo → OpenCV → YOLO → ByteTrack → ID temporal → centroide → Zona → ENTRY/EXIT → permanencia → DB → Dashboard/Heatmap/Reportes.
Para escalar: PostgreSQL + Alembic, Redis/queue, workers GPU por stream, object storage, reverse proxy y observabilidad.
