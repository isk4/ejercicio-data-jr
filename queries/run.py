import sqlite3
from pathlib import Path
from queries import BASE_DIR
import pandas as pd
import re

print("\n- Ejecución consultas SQL")
print(f"\n{'-' * 100}\n")

# Apertura de conexión a db
print("Conectando con la base de datos...")
print(f"\n{'-' * 100}\n")
conn = sqlite3.connect(BASE_DIR / "dw.db")

# Chequeo uso foreign_keys
conn.execute("PRAGMA foreign_keys = ON;")

# Ejecución de consultas
print("Ejecutando consultas...\n")
regex = re.compile(r'(?is)(.*?)(?=\b(?:select|with)\b)') # Regex de obtención de comentarios previos
queries = Path(BASE_DIR / "queries" / "queries.sql").read_text(encoding="utf-8")
statements = [statement.strip() for statement in queries.split(";") if statement.strip()]

for statement in statements:
    # Encontrando pregunta en comentarios previos
    match = regex.search(statement)
    question = match.group(1)
    print(f"{question}\n")

    # Ejecución e impresión resultados de query 
    df = pd.read_sql_query(statement, conn)
    print(df.to_markdown(index=False))
    print(f"\n{'-' * 100}\n")

conn.close()

print("- Finalizó la ejecución de consultas SQL")
print(f"\n{'-' * 100}\n")