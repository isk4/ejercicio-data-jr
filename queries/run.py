import sqlite3
from pathlib import Path
from queries import BASE_DIR
import pandas as pd
import re

print("\n- Ejecución consultas SQL")
print(f"\n{'-' * 100}\n")

print("Conectando con la base de datos...")
print(f"\n{'-' * 100}\n")
# Apertura de conexión a db
conn = sqlite3.connect(BASE_DIR / "dw.db")

conn.execute("PRAGMA foreign_keys = ON;")
queries = Path(BASE_DIR / "queries" / "queries.sql").read_text(encoding="utf-8")

print("Ejecutando consultas...")
statements = [statement.strip() for statement in queries.split(";") if statement.strip()]

regex = re.compile(r'(?is)(.*?)(?=\b(?:select|with)\b)')
for statement in statements:
    print(f"\n{'-' * 100}\n")
    match = regex.search(statement)
    question = match.group(1)

    print(f"{question}\n")
    df = pd.read_sql_query(statement, conn)
    print(df.to_markdown(index=False))

print(f"\n{'-' * 100}\n")
print("- Finalizó la ejecución de consultas SQL")
print(f"\n{'-' * 100}\n")

conn.close()