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

#### 3. Ejecución proceso ETL
```bash
python -m etl.run
```

<em>Desactivar entorno virtual</em>
```bash
deactivate
```