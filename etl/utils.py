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
    # Renombrado de columnas
    df_customers = df_customers.rename(columns={"name": "customer_name"})

    # Cuentas por customer y dataframe final customers
    df_accounts_per_customer = df_customers[["customer_key", "accounts"]]
    df_customers = df_customers[["customer_key", "customer_name", "username", "birthdate"]]

    return df_customers, df_accounts_per_customer

def transform_accounts(df_accounts):
    # Creación surrogate key
    df_accounts["account_key"] = df_accounts.index + 1
    # Renombrado de columnas
    df_accounts = df_accounts.rename(columns={
        "account_id": "account_id_src",
        "limit": "account_limit"
    })

    # Productos por cuenta y dataframe final cuentas
    df_products_per_account = df_accounts[["account_key", "products"]].explode("products")
    df_accounts = df_accounts[["account_key", "account_id_src", "account_limit"]]

    # Creación productos
    df_products = df_products_per_account["products"].drop_duplicates().reset_index(drop=True).to_frame()
    df_products["product_key"] = df_products.index + 1

    # Formateo dataframe para bridge account/product
    df_products_per_account = df_products_per_account.merge(df_products, on="products", how="left")
    df_products_per_account = df_products_per_account[["account_key", "product_key"]]

    return df_accounts, df_products_per_account
