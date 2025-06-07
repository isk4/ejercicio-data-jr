import sqlite3
from pathlib import Path

# Apertura de conexión a db
conn = sqlite3.connect("dw.db")
cursor = conn.cursor()

# Implementación schema.sql
schema_sql = Path("schema/schema.sql").read_text(encoding="utf-8")
cursor.executescript(schema_sql)


conn.commit()

# Validaciones db y foreign keys
cursor.execute("PRAGMA integrity_check;")
if cursor.fetchone()[0] != "ok":
    raise RuntimeError("Falló el chequeo de integridad.")

cursor.execute("PRAGMA foreign_key_check;")
violations = cursor.fetchall()
if violations:
    raise RuntimeError(f"Hubo violaciones de foreign key: {violations}")

# Cierre de conexión a db
conn.close()
