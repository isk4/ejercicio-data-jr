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
    df_customers["birthdate"] = df_customers["birthdate"].map(lambda x: format_date(x["$date"]))
    # Renombrado de columnas
    df_customers = df_customers.rename(columns={"name": "customer_name"})

    # Extracción tiers
    df_tiers_per_customer = df_customers[["customer_key", "tier_and_details"]]
    # Filtrado customers sin tier
    tiers_per_customer_mask = df_tiers_per_customer["tier_and_details"].map(bool)
    df_tiers_per_customer = df_tiers_per_customer[tiers_per_customer_mask]
    # Obtención detalles tiers
    df_tiers_per_customer["tier_and_details"] = df_tiers_per_customer["tier_and_details"].map(lambda x: x.values())
    df_tiers_per_customer = df_tiers_per_customer.explode("tier_and_details")
    # Dataframe final customers
    df_customers = df_customers[["customer_key", "customer_name", "username", "birthdate"]]

    # Creación tiers
    col_tier_and_details = df_tiers_per_customer["tier_and_details"]
    df_tiers = col_tier_and_details.map(lambda x: x["tier"]).to_frame()
    df_tiers = df_tiers.drop_duplicates().reset_index(drop=True)
    df_tiers = df_tiers.rename(columns={"tier_and_details": "tier_name"})
    df_tiers["tier_key"] = df_tiers.index + 1
    
    # Creacion benefits
    df_benefits = col_tier_and_details.map(lambda x: x["benefits"]).explode().to_frame()
    df_benefits = df_benefits.drop_duplicates().reset_index(drop=True)
    df_benefits = df_benefits.rename(columns={"tier_and_details": "benefit_name"})
    df_benefits["benefit_key"] = df_benefits.index + 1

    df_tiers_per_customer["tier_name"] = df_tiers_per_customer["tier_and_details"].map(lambda x: x["tier"])
    df_tiers_per_customer["benefit_name"] = df_tiers_per_customer["tier_and_details"].map(lambda x: x["benefits"])
    df_tiers_per_customer = df_tiers_per_customer.merge(df_tiers, on="tier_name", how="left")
    df_tiers_per_customer = df_tiers_per_customer[["customer_key", "tier_key", "benefit_name"]].explode("benefit_name")
    df_tiers_per_customer = df_tiers_per_customer.merge(df_benefits, on="benefit_name", how="left")

    df_tiers_per_customer = df_tiers_per_customer[["customer_key", "tier_key", "benefit_key"]]
    return df_customers, df_tiers_per_customer

# Transformación dataframe cuentas
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

    return df_accounts, df_products, df_products_per_account
