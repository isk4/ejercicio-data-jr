import sqlite3
import pandas as pd
from pathlib import Path

# Configuración raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Apertura de conexión a db
conn = sqlite3.connect("dw.db")
cursor = conn.cursor()

# Implementación schema.sql
schema_sql = Path("schema/schema.sql").read_text(encoding="utf-8")
cursor.executescript(schema_sql)

# Carga de data desde el origen
df_transactions = pd.read_json(Path(BASE_DIR / "sample_analytics_dataset" / "sample_analytics.transactions.json"))
df_accounts     = pd.read_json(Path(BASE_DIR / "sample_analytics_dataset" / "sample_analytics.accounts.json"))
df_customers    = pd.read_json(Path(BASE_DIR / "sample_analytics_dataset" / "sample_analytics.customers.json"))

print(df_transactions)
print(df_accounts)
print(df_customers)

# Persistencia de inserts
conn.commit()

# Validaciones db y foreign keys
cursor.execute("PRAGMA integrity_check;")
if cursor.fetchone()[0] != "ok":
    raise RuntimeError("Falló el chequeo de integridad de la base de datos.")

cursor.execute("PRAGMA foreign_key_check;")
violations = cursor.fetchall()
if violations:
    raise RuntimeError(f"Hubo violaciones de foreign key: {violations}")

# Cierre de conexión a db
conn.close()
