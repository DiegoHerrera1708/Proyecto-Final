# Proyecto Final - Gestion Deportiva NBA

Aplicacion web desarrollada con Flask para consultar estadisticas de jugadores de la NBA, visualizar metricas avanzadas y permitir que los usuarios registren sus propias estadisticas de partidos.

El proyecto incluye autenticacion de usuarios, endpoints API, analisis de datos con pandas, generacion de graficos y una base de modelos con herencia para representar personas, usuarios y jugadores.

## Funcionalidades principales

- Registro, login, logout y consulta del usuario autenticado.
- Dashboard web con estadisticas de jugadores por temporada.
- API para consultar jugadores paginados por ano.
- API para calcular metricas avanzadas:
  - porcentaje de tiro de campo,
  - porcentaje de tiros de 2 puntos,
  - puntos por partido estimados,
  - volumen de tiro por partido.
- Generacion de graficos con matplotlib, seaborn y plotly.
- Registro privado de estadisticas personales de partidos.
- Tests automaticos con pytest.
- Modelo `Jugador` con herencia desde una clase base `Persona`.

## Tecnologias usadas

- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy
- SQLite
- pandas
- matplotlib
- seaborn
- plotly
- pytest

## Estructura del proyecto

```text
Proyecto-Final/
|-- data/
|   `-- players_stats_by_season_full_details.csv
|-- instance/
|   `-- usuarios.db
|-- src/
|   |-- analytics.py
|   |-- database.py
|   |-- main.py
|   |-- models/
|   |   |-- __init__.py
|   |   |-- jugador.py
|   |   |-- persona.py
|   |   `-- usuario.py
|   |-- static/
|   `-- templates/
|-- tests/
|   |-- test_login.py
|   `-- test_modelos.py
|-- pytest.ini
|-- requirements.txt
`-- README.md
```

## Instalacion

Desde la raiz del proyecto, crea y activa un entorno virtual:

```powershell
python -m venv .env
.\.env\Scripts\Activate.ps1
```

Instala las dependencias:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecucion

Ejecuta la aplicacion desde la raiz del proyecto:

```powershell
.\.env\Scripts\python.exe src\main.py
```

Despues abre en el navegador:

```text
http://127.0.0.1:5000
```

La ruta principal muestra la pagina inicial y el dashboard esta disponible en:

```text
http://127.0.0.1:5000/dashboard
```

## Base de datos

La aplicacion usa SQLite mediante Flask-SQLAlchemy.

Configuracion actual en `src/main.py`:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
```

Las tablas se crean automaticamente al iniciar la aplicacion gracias a:

```python
with app.app_context():
    db.create_all()
```

## Modelos

### Persona

Clase base abstracta definida en `src/models/persona.py`.

Contiene campos comunes:

- `id`
- `nombre`
- `fecha_creacion`

Tambien incluye el metodo `datos_basicos()`.

### Usuario

Modelo definido en `src/models/usuario.py`.

Hereda de:

- `UserMixin`, para integrarse con Flask-Login.
- `Persona`, para reutilizar los campos comunes.

Campos propios:

- `email`
- `password`

Metodos principales:

- `set_password(password)`
- `check_password(password)`

### Jugador

Modelo definido en `src/models/jugador.py`.

Hereda de `Persona`.

Campos propios:

- `equipo`
- `posicion`
- `dorsal`
- `altura_cm`
- `peso_kg`

Metodo principal:

- `to_dict()`

Ejemplo:

```python
from models import Jugador

jugador = Jugador(
    nombre="Pau Gasol",
    equipo="Lakers",
    posicion="Pivot",
    dorsal=16,
    altura_cm=213,
    peso_kg=113,
)
```

## Endpoints principales

### Vistas web

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| GET | `/` | Pagina principal |
| GET | `/dashboard` | Dashboard de estadisticas |

### Datos y graficos

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| GET | `/api/datos-jugadores` | Devuelve jugadores paginados por ano |
| GET | `/api/metricas-avanzadas` | Devuelve metricas avanzadas por ano |
| GET | `/api/generar-graficos` | Genera graficos para un ano |

Ejemplo:

```text
/api/datos-jugadores?ano=2019&pagina=1&items_por_pagina=20
```

### Autenticacion

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| POST | `/api/registrarse` | Registra un usuario |
| POST | `/api/login` | Inicia sesion |
| POST | `/api/logout` | Cierra sesion |
| GET | `/api/usuario-actual` | Devuelve el usuario autenticado |

Ejemplo de login:

```json
{
  "email": "usuario@email.com",
  "password": "password123"
}
```

### Estadisticas personales

Estas rutas requieren usuario autenticado.

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| POST | `/api/guardar-estadisticas` | Guarda estadisticas de un partido |
| GET | `/api/mis-estadisticas` | Lista estadisticas del usuario actual |
| DELETE | `/api/estadistica/<id>` | Elimina una estadistica propia |

Ejemplo para guardar estadisticas:

```json
{
  "rebotes": 8,
  "canastas_tiradas": 15,
  "canastas_encestadas": 7,
  "canastas_3_encestadas": 2,
  "fecha_partido": "2026-05-24",
  "notas": "Buen partido"
}
```

## Tests

El proyecto usa pytest. La configuracion esta en `pytest.ini`:

```ini
[pytest]
pythonpath = src
```

Esto permite importar modulos de `src` directamente desde los tests.

Ejecutar todos los tests:

```powershell
.\.env\Scripts\python.exe -m pytest -q
```

Tests actuales:

- `tests/test_login.py`: validacion basica del login.
- `tests/test_modelos.py`: validacion de herencia entre `Persona`, `Usuario` y `Jugador`.

## Dataset

El dataset principal esta en:

```text
data/players_stats_by_season_full_details.csv
```

El modulo `src/analytics.py` carga este CSV, filtra datos de temporada regular de la NBA y prepara la informacion para el dashboard y la API.

## Notas de desarrollo

- El proyecto debe ejecutarse desde la raiz para que las rutas relativas a `data/` funcionen correctamente.
- Los graficos generados se guardan dentro de las carpetas estaticas del proyecto.
- La base de datos SQLite se crea automaticamente si no existe.
- Algunos tests pueden mostrar un warning relacionado con `datetime.utcnow()`. Es una advertencia de deprecacion, no un fallo de ejecucion.

## Comandos utiles

Activar entorno virtual:

```powershell
.\.env\Scripts\Activate.ps1
```

Ejecutar app:

```powershell
.\.env\Scripts\python.exe src\main.py
```

Ejecutar tests:

```powershell
.\.env\Scripts\python.exe -m pytest -q
```

Ejecutar solo tests de login:

```powershell
.\.env\Scripts\python.exe -m pytest -q tests\test_login.py
```

