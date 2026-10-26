"""Migración aditiva para bases SQLite V7. RESPALDAR antes de ejecutar."""
import argparse
import sqlite3
from pathlib import Path


def migrate(path):
    path=Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    with sqlite3.connect(path) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        with conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS procesamiento (
                id_procesamiento INTEGER PRIMARY KEY,
                id_camara INTEGER NOT NULL REFERENCES camara(id_camara),
                inicio DATETIME NOT NULL, fin DATETIME, estado VARCHAR(20) NOT NULL
            )""")
            conn.execute("CREATE INDEX IF NOT EXISTS ix_procesamiento_id_camara ON procesamiento(id_camara)")
            cols={r[1] for r in conn.execute("PRAGMA table_info(track)")}
            if "id_procesamiento" not in cols:
                conn.execute("ALTER TABLE track ADD COLUMN id_procesamiento INTEGER REFERENCES procesamiento(id_procesamiento)")
            conn.execute("CREATE INDEX IF NOT EXISTS ix_track_id_procesamiento ON track(id_procesamiento)")
            cols={r[1] for r in conn.execute("PRAGMA table_info(evento_zona)")}
            if "motivo_cierre" not in cols:
                conn.execute("ALTER TABLE evento_zona ADD COLUMN motivo_cierre VARCHAR(24)")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("sqlite_path",help="Ruta de la base SQLite previamente respaldada")
    migrate(parser.parse_args().sqlite_path)
