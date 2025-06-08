import sqlite3
import json
from etl import BASE_DIR
from etl.utils import (
    create_tables, 
    get_dataframes, 
    validate_db, 
    format_date, 
    transform_customers,
    transform_accounts,
    transform_transactions,
    generate_dates
)

# # Apertura de conexión a db
# conn = sqlite3.connect(BASE_DIR / "dw.db")
# cursor = conn.cursor()

# # Implementación schema.sql
# create_tables(cursor)

# Carga de data desde el origen
df_transactions, df_accounts, df_customers = get_dataframes()

# Detección account_id duplicados
dup_account_ids = df_accounts["account_id"].duplicated(keep=False)
print("\nSe encontraron ids de cuenta duplicados y estas no serán consideradas:\n")
print(df_accounts[dup_account_ids].to_string())
# Eliminacion de filas con errores
df_accounts = df_accounts[~dup_account_ids]

# Generación de fechas
df_dates = generate_dates()

# Transformación de datos cargados
df_customers, df_accounts_per_customer, df_tiers_per_customer = transform_customers(df_customers)
df_accounts, df_products, df_products_per_account             = transform_accounts(df_accounts)
df_transactions = transform_transactions(df_transactions, df_accounts, df_accounts_per_customer)

print(df_transactions)
# Persistencia de inserts
# conn.commit()

# # Validaciones db y foreign keys
# validate_db(cursor)

# # Cierre de conexión a db
# conn.close()
