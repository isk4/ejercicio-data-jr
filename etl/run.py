import sqlite3
from etl import BASE_DIR
from etl.utils import create_tables, get_dataframes, validate_db

# Apertura de conexión a db
conn = sqlite3.connect(BASE_DIR / "dw.db")
cursor = conn.cursor()

# Implementación schema.sql
create_tables(cursor)

# Carga de data desde el origen
df_transactions, df_accounts, df_customers = get_dataframes()
print(df_transactions)
print(df_accounts)
print(df_customers)

# Persistencia de inserts
conn.commit()

# Validaciones db y foreign keys
validate_db(cursor)

# Cierre de conexión a db
conn.close()
