import sqlite3
import json
from etl import BASE_DIR
from etl.utils import (
    create_tables, 
    get_dataframes, 
    validate_db, 
    format_date, 
    transform_customers,
    transform_accounts
)

# # Apertura de conexión a db
# conn = sqlite3.connect(BASE_DIR / "dw.db")
# cursor = conn.cursor()

# # Implementación schema.sql
# create_tables(cursor)

# Carga de data desde el origen
df_transactions, df_accounts, df_customers = get_dataframes()

df_customers, df_accounts_per_customer = transform_customers(df_customers)
df_accounts, df_products_per_account = transform_accounts(df_accounts)

print(df_products_per_account)

# Persistencia de inserts
# conn.commit()

# # Validaciones db y foreign keys
# validate_db(cursor)

# # Cierre de conexión a db
# conn.close()
