import sqlite3
from pathlib import Path

conn = sqlite3.connect("dw.db")
cursor = conn.cursor()

schema_sql = Path("schema/schema.sql").read_text(encoding="utf-8")
cursor.executescript(schema_sql)

conn.commit()
conn.close()