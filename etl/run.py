import sqlite3
from etl import BASE_DIR
from etl.utils import (
    create_tables, 
    get_dataframes, 
    validate_db, 
    transform_customers,
    transform_accounts,
    transform_transactions,
    generate_dates,
    insert_data
)

print("\n- Inicio script ETL")
print(f"\n{'-' * 100}\n")

# Apertura de conexión a db
print("Conectando con la base de datos...")
print(f"\n{'-' * 100}\n")

conn = sqlite3.connect(BASE_DIR / "dw.db")
cursor = conn.cursor()

# # Implementación schema.sql
print("Creando tablas...")
print(f"\n{'-' * 100}\n")
create_tables(cursor)

# Extracción de data desde el origen
df_transactions, df_accounts, df_customers = get_dataframes()

print(f"\n{'-' * 100}\n")
# Generación de fechas
df_dates = generate_dates()

# Transformación de datos cargados
df_customers, df_tiers, df_benefits, df_accounts_per_customer, df_tiers_per_customer = transform_customers(df_customers)
df_accounts, df_products, df_products_per_account = transform_accounts(df_accounts)
df_transactions = transform_transactions(df_transactions, df_accounts, df_accounts_per_customer)

# Carga de data desde en destino
print(f"\n{'-' * 100}\n")
print("Iniciando insercion de datos...\n")
tables = {
    "Dim_Date": df_dates,
    "Dim_Customer": df_customers,
    "Dim_Account": df_accounts,
    "Dim_Product": df_products,
    "Bridge_Account_Product": df_products_per_account,
    "Dim_Tier": df_tiers,
    "Dim_Benefit": df_benefits,
    "Bridge_Customer_Tier_Benefit": df_tiers_per_customer,
    "Fact_Transaction": df_transactions
}
for table_name, dataframe in tables.items():
    insert_data(table_name, dataframe, cursor, conn)

# Persistencia de inserts
conn.commit()

# # Validaciones db y foreign keys
validate_db(cursor)

# # Cierre de conexión a db
conn.close()

print(f"\n{'-' * 100}\n")
print("- Fin script ETL")
print(f"\n{'-' * 100}\n")