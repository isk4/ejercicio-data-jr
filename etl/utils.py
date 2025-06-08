import pandas as pd
from pathlib import Path
from etl import BASE_DIR
from datetime import datetime, timezone

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
    
# Manejo de formato de fecha de customers
def format_date(date_input):
    if isinstance(date_input, dict):
        date_ms = int(date_input["$numberLong"])
        return pd.to_datetime(date_ms, unit="ms", utc=True).date()
    else:
        return pd.to_datetime(date_input, utc=True).date()

# Transformación dataframe customers
def transform_customers(df_customers):
    # Creación surrogate key
    df_customers["customer_key"] = df_customers.index + 1
    # Formateo de fecha
    df_customers["birthdate"] = df_customers["birthdate"].apply(lambda x: format_date(x["$date"]))

    df_customers = df_customers.rename(columns={"name": "customer_name"})

    # Cuentas por customer y dataframe final
    df_accounts_per_customer = df_customers[["customer_key", "accounts"]]
    df_customers = df_customers[["customer_key", "customer_name", "username", "birthdate"]]

    return df_customers, df_accounts_per_customer
