# ⚡ ETL Pokémon - Primera Generación

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.1-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.23-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.17.0-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.1.0-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.24.3-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-1.12.1-6BA81E?style=for-the-badge)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.8.0-11557C?style=for-the-badge&logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-2.31.0-20232A?style=for-the-badge&logo=python&logoColor=white)

**Pipeline ETL completo para extracción, almacenamiento y visualización de datos de los 150 Pokémon de la Primera Generación usando PokéAPI.**

</div>

---

## 📖 Descripción

Este proyecto implementa un pipeline **ETL (Extract, Transform, Load)** que:

- **Extrae** datos de los 150 Pokémon originales desde la API pública [PokéAPI](https://pokeapi.co/)
- **Transforma** y normaliza la información (stats, tipos, habilidades, descripciones, sprites)
- **Carga** los datos en una base de datos **PostgreSQL** usando SQLAlchemy ORM
- **Visualiza** los datos a través de tres dashboards interactivos construidos con **Streamlit**

---

## 🎯 Objetivos

- Implementar un proceso ETL real usando Python y APIs públicas
- Almacenar datos estructurados en PostgreSQL con migraciones Alembic
- Crear dashboards interactivos profesionales con Streamlit y Plotly
- Aplicar buenas prácticas de ingeniería de datos (logging, métricas, manejo de errores)

---

## 🛠️ Tecnologías

| Herramienta | Versión | Uso |
|---|---|---|
| **Python** | 3.12 | Lenguaje base del proyecto |
| **PostgreSQL** | 16 | Base de datos relacional |
| **SQLAlchemy** | 2.0.23 | ORM para manejo de BD |
| **Alembic** | 1.12.1 | Migraciones de base de datos |
| **Streamlit** | 1.28.1 | Dashboards interactivos |
| **streamlit-lottie** | 0.0.5 | Animaciones Lottie en los dashboards |
| **Plotly** | 5.17.0 | Gráficas interactivas |
| **Pandas** | 2.1.0 | Transformación y análisis de datos |
| **NumPy** | 1.24.3 | Operaciones numéricas |
| **Matplotlib** | 3.8.0 | Gráficas estáticas de análisis |
| **Requests** | 2.31.0 | Peticiones HTTP a PokéAPI y animaciones |
| **psycopg2-binary** | 2.9.9 | Conector Python-PostgreSQL |
| **python-dotenv** | 1.0.0 | Manejo de variables de entorno |
| **openpyxl** | 3.1.2 | Exportación a Excel |
| **PokéAPI** | — | Fuente de datos (API REST pública, sin API key) |
| **WSL Ubuntu** | — | Entorno de desarrollo en Windows |
| **VS Code** | — | Editor de código principal |

---

## 📂 Estructura del Proyecto

```
etl-pokeapi/
├── scripts/
│   ├── database.py         # Configuración de conexión a PostgreSQL
│   ├── models.py           # Modelos SQLAlchemy (tablas Pokemon y MetricasETL)
│   ├── extractor.py        # Extracción de datos desde PokéAPI (genera CSV)
│   ├── extractor_db.py     # Extracción y carga directa a PostgreSQL
│   ├── cargador.py         # Carga de CSV a PostgreSQL
│   ├── visualizador.py     # Gráficas con Matplotlib
│   ├── consultas.py        # Consultas analíticas a la BD
│   └── test_db.py          # Prueba de conexión a PostgreSQL
├── alembic/
│   └── versions/           # Migraciones de base de datos
├── data/
│   ├── pokemon.csv         # Dataset exportado
│   └── pokemon_raw.json    # Datos crudos de la API
├── logs/
│   └── etl.log             # Registro de ejecuciones
├── dashboard_app.py        # Dashboard básico
├── dashboard_advanced.py   # Dashboard avanzado con análisis profundo
├── dashboard_interactive.py # Dashboard interactivo con control total
├── requirements.txt        # Dependencias del proyecto
├── alembic.ini             # Configuración de Alembic
├── .env                    # Variables de entorno (NO se sube a GitHub)
├── .gitignore
└── README.md
```

---

## ⚙️ Instalación y Configuración

### Prerrequisitos

- Python 3.12+
- PostgreSQL 16 instalado y corriendo
- WSL Ubuntu (si usas Windows)

### 1. Clonar el repositorio

```bash
git clone https://github.com/NicolasAlvarez25/Grupo-11-Miner-a-de-datos.git
cd "Grupo-11-Minerìa-de-datos/Proyecto 11 Pokémon/etl-pokeapi"
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Crear la base de datos en PostgreSQL

```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE pokedb;
ALTER USER postgres WITH PASSWORD 'pokemon123';
\q
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
POKEAPI_BASE_URL=https://pokeapi.co/api/v2
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=pokemon123
DB_NAME=pokedb
```

### 5. Aplicar migraciones

```bash
alembic upgrade head
```

### 6. Ejecutar el ETL

```bash
PYTHONPATH=. python scripts/extractor_db.py
```

### 7. Lanzar los dashboards

```bash
# Dashboard básico
PYTHONPATH=. streamlit run dashboard_app.py

# Dashboard avanzado
PYTHONPATH=. streamlit run dashboard_advanced.py

# Dashboard interactivo
PYTHONPATH=. streamlit run dashboard_interactive.py
```

Abre tu navegador en `http://localhost:8501`

---

## 📊 Datos Extraídos

Por cada Pokémon se extraen los siguientes campos:

| Campo | Descripción |
|---|---|
| `id`, `nombre` | Identificador y nombre |
| `tipos`, `habilidades` | Tipos y habilidades (incluyendo ocultas) |
| `hp`, `ataque`, `defensa` | Stats de combate |
| `ataque_especial`, `defensa_especial`, `velocidad` | Stats especiales |
| `es_legendario`, `es_mitico` | Clasificación especial |
| `habitat`, `generacion` | Datos de especie |
| `descripcion` | Descripción del Pokédex |
| `sprite_frente`, `sprite_shiny` | Imágenes del Pokémon |
| `tasa_captura`, `felicidad_base` | Datos de captura |
| `fecha_extraccion` | Timestamp del ETL |

---

## 🗂️ Scripts

| Script | Descripción |
|---|---|
| `extractor_db.py` | Extrae 150 Pokémon de PokéAPI y los guarda en PostgreSQL. Registra métricas de cada ejecución. |
| `extractor.py` | Extrae datos y los guarda en CSV y JSON localmente. |
| `database.py` | Configura la conexión a PostgreSQL usando SQLAlchemy. |
| `models.py` | Define las tablas `pokemon` y `metricas_etl` con SQLAlchemy ORM. |
| `consultas.py` | Consultas analíticas: top atacantes, velocistas, distribución de tipos, legendarios. |
| `test_db.py` | Verifica que la conexión a PostgreSQL funcione correctamente. |
| `visualizador.py` | Genera gráficas de análisis con Matplotlib. |

---

## 📈 Dashboards

### 🟢 Dashboard Básico (`dashboard_app.py`)
- Métricas principales (total, legendarios, mayor ataque, velocidad, HP)
- Filtros por tipo y categoría
- Top 10 por ataque y velocidad
- Pokédex visual con sprites de los 150 Pokémon
- Descarga de datos en CSV

### 🔵 Dashboard Avanzado (`dashboard_advanced.py`)
- Vista general con histogramas y diagramas de caja
- Análisis detallado por tipo con gráfico radar
- Rankings dinámicos por cualquier stat
- Comparador de dos Pokémon con gráfico radar
- Sección de legendarios y míticos con sprites Shiny
- Historial de ejecuciones ETL

### 🔴 Dashboard Interactivo (`dashboard_interactive.py`)
- Filtros avanzados por todos los stats simultáneamente
- Indicadores en tiempo real que responden a los filtros
- Comparador con declaración de ganador automática
- Pokédex visual con búsqueda, filtro por tipo y columnas ajustables
- Soporte para sprites Shiny
- Exportación de datos completos y filtrados en CSV

---

## 👥 Autores

| Nombre |
|---|
| Nicolas Gabriel Álvarez Aguirre |
| Yeison Andres Scarpeta Diaz |

**Institución:** CORHUILA - Ingeniería de Sistemas  
**Materia:** Minería de Datos  
**Grupo:** 11
