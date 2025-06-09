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

    # Detección account_id duplicados
    dup_account_ids = df_accounts["account_id"].duplicated(keep=False)
    print("Se encontraron ids de cuenta duplicados. Las siguientes cuentas no serán consideradas:\n")
    print(df_accounts[dup_account_ids].to_markdown(index=False))

    # Eliminacion de filas de cuentas con errores
    df_accounts = df_accounts[~dup_account_ids]
    
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
    # Guardando cuentas por customer
    df_accounts_per_customer = df_customers.explode("accounts")
    df_accounts_per_customer = df_accounts_per_customer.rename(columns={"accounts": "account_id"})

    # Detección de cuentas con más de un dueño
    multi_owned_accounts = df_accounts_per_customer["account_id"].duplicated(keep=False)
    print("Se encontraron múltiples propietarios para las siguientes cuentas, las que no serán consideradas:\n")
    print(df_accounts_per_customer[multi_owned_accounts][["name", "username", "account_id", ]].to_markdown(index=False))
    # Eliminación de filas con errores
    df_accounts_per_customer = df_accounts_per_customer[~multi_owned_accounts]

    # Renombrado de columnas
    df_customers = df_customers.rename(columns={"name": "customer_name"})
    df_accounts_per_customer = df_accounts_per_customer.rename(columns={"account_id": "account_id_src"})

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

    # Obtención de tiers por cliente
    df_tiers_per_customer["tier_name"] = df_tiers_per_customer["tier_and_details"].map(lambda x: x["tier"])
    df_tiers_per_customer["benefit_name"] = df_tiers_per_customer["tier_and_details"].map(lambda x: x["benefits"])
    df_tiers_per_customer = df_tiers_per_customer.merge(df_tiers, on="tier_name", how="left")
    df_tiers_per_customer = df_tiers_per_customer[["customer_key", "tier_key", "benefit_name"]].explode("benefit_name")
    df_tiers_per_customer = df_tiers_per_customer.merge(df_benefits, on="benefit_name", how="left")

    df_tiers_per_customer = df_tiers_per_customer[["customer_key", "tier_key", "benefit_key"]]
    return df_customers, df_tiers, df_benefits, df_accounts_per_customer, df_tiers_per_customer

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
    df_products = df_products.rename(columns={"products": "product_name"})

    return df_accounts, df_products, df_products_per_account

def generate_dates():
    dates = pd.date_range(start="1950-01-01", end="2025-12-31", freq="D")

    df_dates = pd.DataFrame({"date": dates})
    df_dates["date_key"]   = df_dates["date"].dt.strftime("%Y%m%d").astype(int)
    df_dates["date_month"] = df_dates["date"].dt.month
    df_dates["date_year"]  = df_dates["date"].dt.year
    
    return df_dates[["date_key", "date_year", "date_month"]]

def transform_transactions(df_transactions, df_accounts, df_accounts_per_customer):
    df_transactions = df_transactions[["account_id", "transactions"]].explode("transactions")

    # Asignación de fechas
    dates = df_transactions["transactions"].str.get("date").str.get("$date")
    string_dates = pd.to_datetime(dates, utc=True, errors="coerce")
    number_dates = pd.to_numeric(dates.str.get("$numberLong"), errors="coerce")
    number_dates = pd.to_datetime(number_dates, unit="ms", utc=True, errors="coerce")
    df_transactions["date_key"] = string_dates.fillna(number_dates).dt.strftime("%Y%m%d").astype(int)

    # Extracción de atributos desde objeto
    df_transactions["transaction_code"] = df_transactions["transactions"].str.get("transaction_code")
    df_transactions["symbol"] = df_transactions["transactions"].str.get("symbol")
    df_transactions["amount"] = df_transactions["transactions"].str.get("amount")

    df_transactions = df_transactions.rename(columns={"account_id": "account_id_src"})
    
    # Ignorar transacciones sin cuenta disponible
    df_transactions = df_transactions.merge(df_accounts, on="account_id_src", how="inner")
    df_transactions = df_transactions.merge(df_accounts_per_customer, on="account_id_src", how="left")

    df_transactions["transaction_key"] = df_transactions.index + 1
    return df_transactions[["transaction_key", "account_key", "customer_key", "date_key", "transaction_code", "symbol", "amount"]]

def insert_data(table_name, dataframe, cursor, connection):
    # Inserción de datos de dataframe y log básico
    dataframe.to_sql(
        name=table_name,
        con=connection,
        if_exists="append",
        index=False,       
        chunksize=1000
    )
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    rows = cursor.fetchone()[0]

    print(f"- Se insertaron {rows} filas en la tabla {table_name}\n")
