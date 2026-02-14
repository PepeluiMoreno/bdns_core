# BDNS Core

Libreria compartida del ecosistema BDNS (Base de Datos Nacional de Subvenciones). Proporciona los modelos de datos, autenticacion, logica de negocio y configuracion que consumen tanto `bdns_portal` como `bdns_etl`.

## Que incluye

- **Modelos de base de datos** (SQLAlchemy 2.0): Convocatorias, Concesiones, Beneficiarios, Catalogos, Usuarios y modelos ETL
- **Autenticacion JWT**: Creacion y validacion de tokens, gestion de usuarios con roles (admin, user, viewer)
- **Logica de negocio**: Calculo de subvencion equivalente bruta segun normativa UE (GBER 651/2014)
- **Validacion de minimis**: Control de limites de ayudas de minimis por beneficiario
- **Gestion de base de datos**: Managers sync/async con connection pooling, sesiones FastAPI-ready
- **Configuracion centralizada**: Pydantic Settings con soporte multi-entorno
- **Utilidades**: Interpretacion de NIF/CIF, normalizacion de texto, logging estructurado

## Stack

| Componente | Tecnologia |
|---|---|
| ORM | SQLAlchemy 2.0 + asyncpg |
| Base de datos | PostgreSQL 15 |
| Validacion | Pydantic 2.0 |
| Auth | python-jose (JWT) + passlib (bcrypt) |
| Migraciones | Alembic |
| IDs | UUID v7 (ordenados por tiempo) |

## Estructura

```
src/bdns_core/
├── auth/               # JWT, servicio de usuarios, dependencias FastAPI
│   ├── jwt_auth.py     # Creacion/validacion de tokens, hashing
│   ├── service.py      # CRUD de usuarios, autenticacion
│   ├── models.py       # Schemas Pydantic (UsuarioCreate, Token...)
│   ├── dependencies.py # Inyeccion de dependencias FastAPI
│   └── secrets.py      # Gestion de secretos
├── business/
│   └── equivalencia.py # Calculo ESB y validacion de minimis
├── config/
│   ├── base.py         # BaseSettings compartido
│   ├── etl.py          # Settings especificos ETL
│   └── portal.py       # Settings especificos Portal
├── db/
│   ├── models.py       # Modelos del dominio
│   ├── etl_models.py   # Modelos ETL (EtlJob, EtlExecution, SyncControl)
│   ├── base.py         # Base declarativa SQLAlchemy
│   ├── manager.py      # Managers de conexion sync/async
│   ├── session.py      # Helpers de sesion y generators FastAPI
│   ├── enums.py        # Enumeraciones de BD
│   ├── nif_utils.py    # Interpretacion NIF/CIF (Orden EHA/451/2008)
│   ├── utils.py        # Normalizacion de texto, busqueda de organos
│   ├── bootstrap/      # Scripts SQL de inicializacion
│   └── migrations/     # Migraciones Alembic
└── logging.py          # JSON (produccion) / colores (desarrollo)
```

## Instalacion

```bash
pip install -e .
```

## Uso

```python
# Base de datos (async)
from bdns_core.db.manager import db_manager
from bdns_core.db.models import Beneficiario

async with db_manager.session() as session:
    result = await session.execute(select(Beneficiario))
    beneficiarios = result.scalars().all()

# Base de datos (sync)
from bdns_core.db.manager import sync_db_manager

with sync_db_manager.session() as session:
    beneficiarios = session.query(Beneficiario).all()

# Autenticacion
from bdns_core.auth.jwt_auth import create_token_pair, verify_token

tokens = create_token_pair("user@example.com", role="admin")
user = verify_token(tokens.access_token)

# Calculo de equivalencia
from bdns_core.business.equivalencia import calcular_importe_equivalente

equivalente = calcular_importe_equivalente(
    importe_nominal=100000.0,
    fecha_concesion=date(2024, 1, 1),
    instrumento="prestamo",
    metadata={"plazo_meses": 60, "tipo_interes": 0.5}
)
```

## Variables de entorno

```bash
ENVIRONMENT=development            # development | production
DATABASE_URL=postgresql://user:pass@localhost:5432/bdns
JWT_SECRET_KEY=cambiar-en-produccion
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
POOL_SIZE=20
POOL_MAX_OVERFLOW=10
LOG_LEVEL=INFO
```

## Esquemas de base de datos

| Esquema | Contenido |
|---|---|
| `bdns` | Convocatorias, concesiones, beneficiarios, catalogos, usuarios |
| `bdns_etl` | Jobs ETL, ejecuciones, control de sincronizacion |

## Modelos principales

- **Convocatoria**: Convocatorias de subvenciones con relaciones M2M (instrumentos, regiones, sectores...)
- **Concesion**: Concesiones otorgadas con importes nominal y equivalente, particionadas por ano/regimen
- **Beneficiario**: Entidades beneficiarias con NIF, forma juridica y tipo
- **Usuario**: Usuarios del sistema con roles y vinculacion Telegram
- **Catalogos**: Finalidad, Fondo, Instrumento, Objetivo, Organo, Region, Reglamento, RegimenAyuda, Sector...

## Uso en otros proyectos

Tanto `bdns_portal` como `bdns_etl` dependen de esta libreria:

```bash
pip install -e ../bdns_core
```

## Licencia

MIT
