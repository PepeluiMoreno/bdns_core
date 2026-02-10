# BDNS Core

Librería compartida para el ecosistema BDNS (Base de Datos Nacional de Subvenciones).

## 📦 Componentes

Esta librería proporciona funcionalidad compartida entre `bdns_portal` y `bdns_etl`:

- **`db/`** - Gestión de base de datos
  - Modelos SQLAlchemy (dominio + ETL)
  - Database managers (sync/async)
  - Utilidades de sesión y conexión

- **`auth/`** - Autenticación JWT
  - Generación y validación de tokens
  - Password hashing con bcrypt
  - Sistema de refresh tokens

- **`business/`** - Lógica de negocio
  - Cálculo de equivalencias de subvenciones
  - Validación de límites de minimis

## 🚀 Instalación

```bash
cd bdns_core
pip install -e .
```

## ⚙️ Configuración

### Variables de Entorno

El sistema carga diferentes archivos de configuración según la variable `ENVIRONMENT`:

- **`ENVIRONMENT=development`** (default) → carga `.env.development`
- **`ENVIRONMENT=production`** → carga `.env`

#### Configuración para Desarrollo

1. Copia el archivo de ejemplo:
```bash
cp .env.example .env.development
```

2. Edita `.env.development` con tus valores locales

3. Las variables principales son:

```bash
# Environment
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bdns

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Connection Pool
POOL_SIZE=20
POOL_MAX_OVERFLOW=10
```

Ver [.env.example](.env.example) para la lista completa de variables.

## 📖 Uso

### Database Manager

```python
from bdns_core.db.manager import db_manager, sync_db_manager
from bdns_core.db.models import Beneficiario

# Async
async with db_manager.session() as session:
    result = await session.execute(select(Beneficiario))
    beneficiarios = result.scalars().all()

# Sync
with sync_db_manager.session() as session:
    beneficiarios = session.query(Beneficiario).all()
```

### JWT Authentication

```python
from bdns_core.auth.jwt_auth import create_token_pair, verify_token

# Crear tokens
tokens = create_token_pair(username="user@example.com", role="admin")
print(tokens.access_token)
print(tokens.refresh_token)

# Verificar token
user = verify_token(access_token)
if user:
    print(f"Usuario: {user.username}, Rol: {user.role}")
```

### Cálculo de Equivalencias

```python
from bdns_core.business.equivalencia import calcular_importe_equivalente
from datetime import date

# Subvención directa
equivalente = calcular_importe_equivalente(
    importe_nominal=10000.0,
    fecha_concesion=date(2023, 1, 1)
)

# Préstamo (placeholder actual)
equivalente = calcular_importe_equivalente(
    importe_nominal=100000.0,
    fecha_concesion=date(2023, 1, 1),
    instrumento="prestamo",
    metadata={"plazo_meses": 60, "tipo_interes": 0.5}
)
```

## 🗂️ Estructura

```
bdns_core/
├── src/bdns_core/
│   ├── auth/              # Autenticación JWT
│   │   ├── __init__.py
│   │   └── jwt_auth.py
│   ├── business/          # Lógica de negocio
│   │   └── equivalencia.py
│   ├── db/                # Base de datos
│   │   ├── __init__.py
│   │   ├── base.py        # Base declarativa
│   │   ├── manager.py     # Connection managers
│   │   ├── models.py      # Modelos de dominio
│   │   ├── etl_models.py  # Modelos ETL
│   │   ├── enums.py       # Enumeraciones
│   │   ├── nif_utils.py   # Utilidades NIF
│   │   ├── session.py     # Helpers de sesión
│   │   └── utils.py       # Utilidades varias
│   └── __init__.py
├── .env.example           # Template de variables
├── .env.development       # Variables de desarrollo (git-ignored)
├── pyproject.toml         # Configuración del paquete
└── README.md
```

## 🔐 Seguridad

⚠️ **IMPORTANTE**: Nunca commits archivos `.env` al repositorio.

- `.env.development` y `.env` están en `.gitignore`
- `.env.example` es el único archivo de entorno versionado
- En producción, usa variables de entorno del sistema o secrets managers

## 📝 Notas de Desarrollo

### TODOs Pendientes

Ver comentarios `TODO` en el código para funcionalidades pendientes:

1. **Equivalencias** (`business/equivalencia.py`):
   - Implementar cálculo VAN real para préstamos
   - Implementar primas de garantía según rating
   - Consultar tablas oficiales de tipos de referencia

2. **Validación de minimis**:
   - Implementar consultas reales a BD (actualmente placeholder)

## 🤝 Uso en otros proyectos

Los proyectos `bdns_portal` y `bdns_etl` usan esta librería instalándola en modo editable:

```bash
pip install -e ../bdns_core
```

Esto permite que los cambios en `bdns_core` se reflejen inmediatamente en los proyectos que la usan.
