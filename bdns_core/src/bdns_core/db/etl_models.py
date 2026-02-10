"""
Modelos de base de datos para control y monitoreo del ETL.

Estos modelos se mantienen separados de models.py para mejorar la claridad:
- models.py: Modelos de dominio de negocio (beneficiarios, concesiones, catálogos)
- etl_models.py: Modelos de infraestructura ETL (jobs, executions, control)
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Text,
    Index,
    UniqueConstraint,
)
from .base import Base
from .models import UUIDMixin, AuditMixin


# =========================================================
# ETL JOB TRACKING
# =========================================================

class EtlJob(UUIDMixin, Base):
    """
    Registro de jobs individuales del ETL (usado en ETL por lotes).

    Cada job representa una unidad de trabajo:
    - entity: 'concesiones', 'convocatorias', etc.
    - year: Año a procesar
    - mes: Mes (opcional)
    - tipo: 'A' (anual), 'M' (mensual), etc.
    - stage: 'extract', 'transform', 'load'
    - status: 'pending', 'running', 'completed', 'failed'
    """
    __tablename__ = "etl_job"

    entity = Column(String(50), nullable=False)
    finished_at = Column(DateTime)
    last_error = Column(Text)
    mes = Column(Integer)
    retries = Column(Integer, nullable=False, default=0)
    stage = Column(String(20), nullable=False)
    started_at = Column(DateTime)
    status = Column(String(20), nullable=False, default="pending")
    tipo = Column(String(1))
    updated_at = Column(DateTime, nullable=False, server_default="now()", onupdate="now()")
    year = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("entity", "year", "mes", "tipo", "stage", name="uq_etl_job"),
        Index("ix_etl_job_pending", "status", "stage"),
        {'schema': 'etl_admin'}
    )


# =========================================================
# ETL EXECUTION HISTORY
# =========================================================

class EtlExecution(UUIDMixin, Base):
    """
    Registro de ejecuciones completas del ETL (seeding y sync).

    Cada registro representa una ejecución completa del proceso ETL:
    - execution_type: 'seeding' (carga inicial), 'sync' (sincronización incremental)
    - entity: Entidad procesada (opcional, None si es full)
    - year: Año procesado (opcional)
    - status: 'running', 'completed', 'failed'

    Métricas:
    - records_processed: Total de registros procesados
    - records_inserted: Registros nuevos insertados
    - records_updated: Registros actualizados
    - records_errors: Registros con errores
    - execution_time_seconds: Duración de la ejecución
    """
    __tablename__ = "etl_execution"
    __table_args__ = {'schema': 'etl_admin'}

    created_at = Column(DateTime, nullable=False, server_default="now()")
    current_phase = Column(String(50))  # Fase actual: extracting, transforming, loading, validating
    current_operation = Column(Text)  # Operación específica en curso
    entrypoint = Column(String(255))  # Script/entrypoint que se está ejecutando
    entity = Column(String(50))
    error_message = Column(Text)
    execution_time_seconds = Column(Integer)
    execution_type = Column(String(20), nullable=False, index=True)
    finished_at = Column(DateTime)
    progress_percentage = Column(Integer, default=0)  # Porcentaje de progreso (0-100)
    records_errors = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_processed = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, index=True)
    window_end = Column(DateTime)
    window_months = Column(Integer)
    window_start = Column(DateTime)
    year = Column(Integer)


# =========================================================
# SYNC CONTROL
# =========================================================

class SyncControl(UUIDMixin, Base, AuditMixin):
    """
    Control de sincronizaciones incrementales con la API BDNS.

    Cada registro representa una ventana de sincronización:
    - fecha_desde, fecha_hasta: Rango de fechas sincronizado
    - estado: 'running', 'completed', 'failed'

    Detecta cambios respecto a la base de datos local:
    - inserts_detectados: Nuevas concesiones/convocatorias
    - updates_detectados: Registros modificados
    - deletes_detectados: Registros eliminados en origen
    """
    __tablename__ = "sync_control"
    __table_args__ = {'schema': 'etl_admin'}

    deletes_detectados = Column(Integer, default=0)
    error = Column(Text)
    estado = Column(String(20), default="running", index=True)
    fecha_desde = Column(Date, nullable=False)
    fecha_hasta = Column(Date, nullable=False)
    inserts_detectados = Column(Integer, default=0)
    updates_detectados = Column(Integer, default=0)
