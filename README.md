## Requisitos

- Python >= 3.9
- pip

## Instrucciones

#### 1. (Opcional) Crear y activar entorno virtual
- <em>Linux/macOS</em>
```bash
python -m venv .venv
source .venv/bin/activate
```

- <em>Windows (PowerShell)</em>
```bash
python -m venv .venv
.venv\Scripts\activate
```
---

#### 2. Instalación de dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
---

#### 3. Ejecución proceso ETL
```bash
python3 -m etl.run
# O dependiendo del entorno:
# python -m etl.run
```
---

#### 4. Ejecución de consultas SQL
```bash
python3 -m queries.run
# O dependiendo del entorno:
# python -m queries.run
```
---

#### 5. Desactivar entorno virtual
```bash
deactivate
```