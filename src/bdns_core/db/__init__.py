# bdns_core/db/__init__.py
from bdns_core.db.base import Base
from bdns_core.db.models import *
from bdns_core.db.etl_models import *  # Modelos de control ETL
from bdns_core.db.manager import *
from .session import get_db, get_db_context, engine, async_engine

__all__ = [
    "AsyncDatabaseManager",
    "Base",
    "Beneficiario",
    "Concesion",
    "Convocatoria",
    "DocumentoConvocatoria",
    "AnuncioConvocatoria",
    "EtlExecution",
    "EtlJob",
    "Finalidad",
    "Fondo",
    "FormaJuridica",
    "Instrumento",
    "Objetivo",
    "Organo",
    # "Programa",                 # ❌ ELIMINADO (no existe)
    "Pseudonimo",
    "Region",
    "RegimenAyuda",
    "Reglamento",
    "SectorActividad",
    "SectorProducto",
    "SyncControl",
    "SyncDatabaseManager",
    "TipoBeneficiario",
    "get_db",
    "get_db_context", 
    "engine",
    "async_engine",
]
