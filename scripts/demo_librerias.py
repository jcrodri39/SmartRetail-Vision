"""
Demostración de las dos librerías aplicadas, sin cámara ni base de datos.

    python -m scripts.demo_librerias

1. LogBack -> logging : escribe logs/smartretail.log, logs/errores.log y logs/rendimiento.csv
2. Apache POI -> openpyxl: genera reporte_demo.xlsx con el mismo formato que /reports/download.xlsx

Los eventos se generan con semilla fija y se marcan como DATOS DE PRUEBA: sirven
para validar el funcionamiento, no son resultados experimentales del proyecto.
"""
import logging
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

from app.core.logging_config import RegistroRendimiento, configurar_logging, detener_logging, sesion_log
from app.services.excel_report import build_workbook

ZONAS = ["Entrada", "Frutas y verduras", "Panadería", "Lácteos", "Cajas"]
log = logging.getLogger("smartretail.demo")


def eventos_de_prueba(n_tracks: int = 60, semilla: int = 7) -> list[dict]:
    rnd = random.Random(semilla)
    inicio = datetime(2026, 10, 10, 9, 0)
    eventos, id_evento = [], 1
    for track in range(1, n_tracks + 1):
        t = inicio + timedelta(minutes=rnd.randint(0, 8 * 60))
        for zona in ["Entrada"] + rnd.sample(ZONAS[1:4], rnd.randint(1, 3)) + ["Cajas"]:
            dur = rnd.randint(8, 240)
            abierto = track > n_tracks - 3 and zona == "Cajas"   # presencias aún abiertas
            eventos.append({"id_evento": id_evento, "track": track, "zona": zona, "entrada": t,
                            "salida": None if abierto else t + timedelta(seconds=dur),
                            "permanencia_seg": 0 if abierto else float(dur)})
            id_evento += 1
            t += timedelta(seconds=dur + rnd.randint(5, 60))
    return eventos


def agregar_como_dashboard(eventos: list[dict]) -> dict:
    """Mismas reglas que app/services/metrics.py y reports.py."""
    filas, todas = [], []
    for i, z in enumerate(ZONAS, start=1):
        ev = [e for e in eventos if e["zona"] == z]
        vals = [e["permanencia_seg"] for e in ev if e["permanencia_seg"]]
        todas += vals
        filas.append({"id": i, "zona": z, "flujo": len(ev),
                      "permanencia": round(sum(vals) / len(vals), 1) if vals else 0,
                      "ocupacion": sum(1 for e in ev if e["salida"] is None)})
    top_f = max(filas, key=lambda r: r["flujo"])
    top_d = max(filas, key=lambda r: r["permanencia"])
    return {"flujo": len(eventos), "permanencia": round(sum(todas) / len(todas), 1) if todas else 0,
            "ocupacion": sum(r["ocupacion"] for r in filas), "tracks": len({e["track"] for e in eventos}),
            "detecciones": 0, "zonas": filas,
            "advanced": {"confidence_avg": 0.0, "completed_visits": sum(1 for e in eventos if e["salida"]),
                         "dwell_max": max(todas) if todas else 0, "zones_count": len(filas),
                         "top_flow": top_f["zona"], "top_flow_value": top_f["flujo"],
                         "top_dwell": top_d["zona"], "top_dwell_value": top_d["permanencia"]}}


def main() -> None:
    configurar_logging("logs", "INFO")
    log.info("Demo iniciada")
    log.info("Fuente registrada: %s", "rtsp://admin:Clave123@192.168.1.20:554/stream1")
    log.info("Inicio de sesión correcto: %s (rol %s)", "analyst@smartretail.local", "ANALYST")

    with sesion_log(f"cam1-{datetime.utcnow():%Y%m%dT%H%M%S}"):
        perf = RegistroRendimiento(cada_n_frames=50)
        for frame in range(1, 151):            # simulación de 150 cuadros
            with perf.medir("yolo_tracking"):
                time.sleep(0.004)
            with perf.medir("zonas_eventos_bd"):
                time.sleep(0.001)
            if frame == 120:
                log.warning("Frame %d no pudo leerse; se continúa con el siguiente (UC004 flujo 2A)", frame)
            perf.frame_procesado(personas=random.randint(2, 6))
        try:
            raise ConnectionError("la cámara dejó de responder")
        except ConnectionError:
            log.exception("Fuente no disponible; se interrumpe el procesamiento (UC004 flujo 1A)")

    eventos = eventos_de_prueba()
    data = agregar_como_dashboard(eventos)
    meta = {"tienda": "Tienda Demo", "generado_por": "Analista", "generado": datetime.now(), "id_reporte": "DEMO",
            "store_id": 1, "modelo": "yolo11n.pt", "tracker": "bytetrack.yaml", "conf": 0.35, "iou": 0.70,
            "eventos_exportados": len(eventos), "datos_de_prueba": True}
    destino = Path("reporte_demo.xlsx")
    destino.write_bytes(build_workbook(data, eventos, meta))
    log.info("Reporte Excel de prueba generado: %s (%d eventos)", destino, len(eventos))
    detener_logging()


if __name__ == "__main__":
    main()
