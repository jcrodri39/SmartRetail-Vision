import logging
import threading

from app.core.logging_config import (ContextoSesionFilter, PrivacidadFilter, RegistroRendimiento,
                                     construir_configuracion, sesion_log)


def _registro(msg, *args):
    return logging.LogRecord("smartretail.test", logging.INFO, __file__, 1, msg, args, None)


def test_enmascara_credenciales_rtsp():
    r = _registro("Fuente: %s", "rtsp://admin:Clave123@192.168.1.20:554/stream1")
    PrivacidadFilter().filter(r)
    assert r.getMessage() == "Fuente: rtsp://***:***@192.168.1.20:554/stream1"


def test_enmascara_correo_y_conserva_dominio():
    r = _registro("Login de analyst@smartretail.local")
    PrivacidadFilter().filter(r)
    assert r.getMessage() == "Login de ***@smartretail.local"


def test_mensaje_sin_datos_sensibles_no_cambia():
    r = _registro("Zona %s creada", "Cajas")
    PrivacidadFilter().filter(r)
    assert r.args == ("Cajas",) and r.getMessage() == "Zona Cajas creada"


def test_contexto_de_sesion_por_hilo():
    vistos = {}

    def trabajo(nombre):
        with sesion_log(nombre):
            r = _registro("x")
            ContextoSesionFilter().filter(r)
            vistos[nombre] = r.id_sesion

    hilos = [threading.Thread(target=trabajo, args=(f"cam{i}",)) for i in range(3)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    assert vistos == {"cam0": "cam0", "cam1": "cam1", "cam2": "cam2"}
    r = _registro("fuera")
    ContextoSesionFilter().filter(r)
    assert r.id_sesion == "-"


def test_configuracion_equivale_a_appenders_de_logback(tmp_path):
    cfg = construir_configuracion(tmp_path)
    h = cfg["handlers"]
    assert h["archivo_app"]["class"].endswith("RotatingFileHandler")          # política por tamaño
    assert h["archivo_errores"]["class"].endswith("TimedRotatingFileHandler")  # política por tiempo
    assert h["archivo_errores"]["level"] == "ERROR"                            # ThresholdFilter
    assert cfg["loggers"]["smartretail.rendimiento"]["propagate"] is False     # additivity=false


def test_registro_rendimiento_escribe_fps_y_latencia(caplog):
    perf = RegistroRendimiento(cada_n_frames=2)
    with caplog.at_level(logging.INFO, logger="smartretail.rendimiento"):
        logging.getLogger("smartretail.rendimiento").addHandler(caplog.handler)
        for _ in range(2):
            with perf.medir("yolo_tracking"):
                pass
            perf.frame_procesado(personas=3)
    linea = caplog.records[-1].getMessage()
    assert linea.startswith("frames=2;fps=") and "personas_prom=3.0" in linea and "yolo_tracking=" in linea
