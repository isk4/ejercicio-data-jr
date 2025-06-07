import pandas as pd
from pathlib import Path
from etl import BASE_DIR

# Implementación schema.sql
def create_tables(cursor):
    schema_sql = Path(BASE_DIR / "schema" / "schema.sql").read_text(encoding="utf-8")
    cursor.executescript(schema_sql)

# Carga de data desde el origen
def get_dataframes():
    df_transactions = pd.read_json(Path(BASE_DIR / "sample_analytics_dataset" / "sample_analytics.transactions.json"))
    df_accounts     = pd.read_json(Path(BASE_DIR / "sample_analytics_dataset" / "sample_analytics.accounts.json"))
    df_customers    = pd.read_json(Path(BASE_DIR / "sample_analytics_dataset" / "sample_analytics.customers.json"))
    
    return df_transactions, df_accounts, df_customers

# Validaciones db y foreign keys
def validate_db(cursor):
    cursor.execute("PRAGMA integrity_check;")
    if cursor.fetchone()[0] != "ok":
        raise RuntimeError("Falló el chequeo de integridad de la base de datos.")

    cursor.execute("PRAGMA foreign_key_check;")
    violations = cursor.fetchall()
    if violations:
        raise RuntimeError(f"Hubo violaciones de foreign key: {violations}")