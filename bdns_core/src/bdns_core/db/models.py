from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Index,
    Table,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from uuid_utils import uuid7
from .base import Base


# =========================================================
# MIXINS
# =========================================================

class UUIDMixin:
    """PK UUID v7 (time-ordered) para todas las tablas."""
    id = Column(
        Uuid,
        primary_key=True,
        default=uuid7,
        server_default=text("uuid_generate_v7()"),
    )


class AuditMixin:
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    created_by = Column(String(50))
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(50))


# =========================================================
# CATALOGOS
# =========================================================

class Finalidad(UUIDMixin, Base):
    __tablename__ = "finalidad"

    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String)
    descripcion_norm = Column(String)


class Fondo(UUIDMixin, Base):
    __tablename__ = "fondo"

    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String)
    descripcion_norm = Column(String)


class FormaJuridica(UUIDMixin, Base):
    __tablename__ = "forma_juridica"

    codigo = Column(String, nullable=False, unique=True, index=True)
    codigo_natural = Column(String(1), nullable=False, index=True)
    descripcion = Column(String, nullable=False)
    descripcion_norm = Column(String, nullable=False, index=True)
    es_persona_fisica = Column(Boolean, nullable=False, default=False)
    tipo = Column(String, nullable=False)


class Instrumento(UUIDMixin, Base):
    __tablename__ = "instrumento"

    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String)
    descripcion_norm = Column(String)


class Objetivo(UUIDMixin, Base):
    __tablename__ = "objetivo"

    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String)
    descripcion_norm = Column(String)


class Organo(UUIDMixin, Base):
    __tablename__ = "organo"

    codigo = Column(String, nullable=False, unique=True, index=True)
    hijos = relationship("Organo", back_populates="padre")
    id_padre = Column(Uuid, ForeignKey("organo.id"))
    nivel1 = Column(String)
    nivel1_norm = Column(String)
    nivel2 = Column(String)
    nivel2_norm = Column(String)
    nivel3 = Column(String)
    nivel3_norm = Column(String)
    nombre = Column(String, nullable=False)
    padre = relationship("Organo", remote_side="Organo.id", back_populates="hijos")
    tipo = Column(String, nullable=False)

    __table_args__ = (
        Index("ix_organo_niveles", "nivel1_norm", "nivel2_norm", "nivel3_norm"),
    )


class Reglamento(UUIDMixin, Base):
    __tablename__ = "reglamento"

    ambito = Column(String, nullable=False)
    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String)
    descripcion_norm = Column(String)


class Region(UUIDMixin, Base):
    __tablename__ = "region"

    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String, nullable=False)
    descripcion_norm = Column(String, nullable=False)
    hijos = relationship("Region", back_populates="padre")
    id_padre = Column(Uuid, ForeignKey("region.id"))
    padre = relationship("Region", remote_side="Region.id", back_populates="hijos")


class RegimenAyuda(UUIDMixin, Base):
    __tablename__ = "regimen_ayuda"

    descripcion = Column(String, nullable=False, unique=True)
    descripcion_norm = Column(String, nullable=False, unique=True, index=True)


class SectorActividad(UUIDMixin, Base):
    __tablename__ = "sector_actividad"

    codigo = Column(String, nullable=False, unique=True, index=True)
    descripcion = Column(String, nullable=False)
    descripcion_norm = Column(String, index=True)
    hijos = relationship("SectorActividad", back_populates="padre")
    id_padre = Column(Uuid, ForeignKey("sector_actividad.id"))
    padre = relationship("SectorActividad", remote_side="SectorActividad.id", back_populates="hijos")


class SectorProducto(UUIDMixin, Base):
    __tablename__ = "sector_producto"

    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String)
    descripcion_norm = Column(String)


class TipoBeneficiario(UUIDMixin, Base):
    __tablename__ = "tipo_beneficiario"

    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String)
    descripcion_norm = Column(String)


# =========================================================
# BENEFICIARIOS
# =========================================================

class Beneficiario(UUIDMixin, Base, AuditMixin):
    __tablename__ = "beneficiario"

    forma_juridica = relationship("FormaJuridica")
    forma_juridica_id = Column(Uuid, ForeignKey("forma_juridica.id"))
    nif = Column(String, index=True)
    nombre = Column(String, nullable=False)
    nombre_norm = Column(String, nullable=False)
    pseudonimos = relationship("Pseudonimo", back_populates="beneficiario", cascade="all, delete-orphan")
    tipo_beneficiario = relationship("TipoBeneficiario")
    tipo_beneficiario_id = Column(Uuid, ForeignKey("tipo_beneficiario.id"))

    @property
    def es_entidad_publica(self) -> bool:
        """Determina si el beneficiario es una entidad pública."""
        if not self.forma_juridica:
            return False
        return self.forma_juridica.tipo == "publica"

    @property
    def es_persona_fisica(self) -> bool:
        """Determina si el beneficiario es una persona física basándose en su forma jurídica."""
        if not self.forma_juridica:
            return False
        return self.forma_juridica.es_persona_fisica

    @property
    def es_persona_juridica(self) -> bool:
        """Determina si el beneficiario es una persona jurídica."""
        if not self.forma_juridica:
            return False
        return not self.forma_juridica.es_persona_fisica and self.forma_juridica.tipo != "desconocido"


class Pseudonimo(UUIDMixin, Base):
    __tablename__ = "pseudonimo"

    beneficiario = relationship("Beneficiario", back_populates="pseudonimos")
    beneficiario_id = Column(Uuid, ForeignKey("beneficiario.id"), nullable=False)
    pseudonimo = Column(String, nullable=False)
    pseudonimo_norm = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("beneficiario_id", "pseudonimo_norm", name="uq_beneficiario_pseudonimo"),
    )


# =========================================================
# CONVOCATORIAS Y CONCESIONES
# =========================================================

class Convocatoria(UUIDMixin, Base, AuditMixin):
    __tablename__ = "convocatoria"

    codigo_bdns = Column(String, nullable=False, unique=True, index=True)
    descripcion = Column(Text)
    fecha_recepcion = Column(Date)
    organo = relationship("Organo")
    organo_id = Column(Uuid, ForeignKey("organo.id"))
    presupuesto_total = Column(Float)
    reglamento = relationship("Reglamento")
    reglamento_id = Column(Uuid, ForeignKey("reglamento.id"))


class Concesion(Base, AuditMixin):
    """
    Tabla particionada jerárquicamente (RANGE + LIST) para optimizar queries.

    PARTICIONADO JERÁRQUICO:
    ========================
    Nivel 1: RANGE por fecha_concesion (anual: 2015, 2016, 2017, ...)
    Nivel 2: LIST por regimen_tipo ('minimis', 'ayuda_estado', 'ordinaria', etc.)

    Beneficios:
    - Partition pruning en dos dimensiones (año + régimen)
    - Queries como "minimis de 2024" escanean solo 1 subpartición
    - Permite borrar/analizar por ejercicio y régimen específico

    NOTAS:
    - UUIDMixin no se usa aquí porque el PK es compuesto (id, fecha_concesion, regimen_tipo)
    - regimen_tipo es campo denormalizado para permitir LIST partitioning
    - Las columnas del PK deben incluir todas las claves de particionamiento

    Estructura de particiones:
    - concesion_2015_minimis, concesion_2015_ayuda_estado, concesion_2015_ordinaria, ...
    - concesion_2016_minimis, concesion_2016_ayuda_estado, concesion_2016_ordinaria, ...
    - etc.
    """
    __tablename__ = "concesion"

    # PK compuesto: id + fecha_concesion + regimen_tipo (requerido para particionamiento jerárquico)
    id = Column(Uuid, primary_key=True, default=uuid7, server_default=text("uuid_generate_v7()"))
    fecha_concesion = Column(Date, nullable=False, primary_key=True)
    regimen_tipo = Column(String(20), nullable=False, default="desconocido", primary_key=True)

    # Campos de negocio (alfabético)
    beneficiario = relationship("Beneficiario")
    beneficiario_id = Column(Uuid, ForeignKey("beneficiario.id"), nullable=False)
    convocatoria = relationship("Convocatoria")
    convocatoria_id = Column(Uuid, ForeignKey("convocatoria.id"), nullable=False)
    id_concesion = Column(String, nullable=False)
    importe_equivalente = Column(Float)
    importe_nominal = Column(Float)
    regimen_ayuda = relationship("RegimenAyuda")
    regimen_ayuda_id = Column(Uuid, ForeignKey("regimen_ayuda.id"))

    __table_args__ = (
        UniqueConstraint("id_concesion", "fecha_concesion", "regimen_tipo", name="uq_concesion_id_fecha"),
        Index("ix_concesion_id_concesion", "id_concesion", "fecha_concesion"),
        Index("ix_concesion_regimen_fecha", "regimen_tipo", "fecha_concesion"),
        {'postgresql_partition_by': 'RANGE (fecha_concesion)'}
    )

    @property
    def es_ayuda_estado(self) -> bool:
        if not self.regimen_ayuda or not self.regimen_ayuda.descripcion_norm:
            return False
        return self.regimen_ayuda.descripcion_norm == "ayuda de estado"

    @property
    def es_minimis(self) -> bool:
        if not self.regimen_ayuda or not self.regimen_ayuda.descripcion_norm:
            return False
        return self.regimen_ayuda.descripcion_norm == "minimis"

    @property
    def organo_concedente(self) -> str:
        """Retorna el UUID del órgano concedente."""
        return self.convocatoria.organo_id
