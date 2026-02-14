# bdns_core/db/models.py
from typing import Optional
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, Boolean, Text,
    ForeignKey, Index, Table, UniqueConstraint, Uuid, text
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
# CATALOGOS (definidos primero, antes de las tablas puente)
# =========================================================

class Finalidad(UUIDMixin, Base):
    __tablename__ = "finalidad"
    __table_args__ = {'schema': 'bdns'}

    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String, nullable=False)
    descripcion_norm = Column(String, index=True)


class Fondo(UUIDMixin, Base):
    __tablename__ = "fondo"
    __table_args__ = {'schema': 'bdns'}

    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String, nullable=False)
    descripcion_norm = Column(String, index=True)


class FormaJuridica(UUIDMixin, Base):
    __tablename__ = "forma_juridica"
    __table_args__ = {'schema': 'bdns'}

    codigo = Column(String, nullable=False, unique=True, index=True)
    codigo_natural = Column(String(1), nullable=False, index=True)
    descripcion = Column(String, nullable=False)
    descripcion_norm = Column(String, nullable=False, index=True)
    es_persona_fisica = Column(Boolean, nullable=False, default=False)
    tipo = Column(String, nullable=False)


class Instrumento(UUIDMixin, Base):
    __tablename__ = "instrumento"
    __table_args__ = {'schema': 'bdns'}

    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String, nullable=False)
    descripcion_norm = Column(String, index=True)


class Objetivo(UUIDMixin, Base):
    __tablename__ = "objetivo"
    __table_args__ = {'schema': 'bdns'}

    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String, nullable=False)
    descripcion_norm = Column(String, index=True)


class Organo(UUIDMixin, Base):
    __tablename__ = "organo"
    __table_args__ = (
        Index("ix_organo_niveles", "nivel1_norm", "nivel2_norm", "nivel3_norm"),
        {'schema': 'bdns'}
    )

    codigo = Column(String, nullable=False, unique=True, index=True)
    id_padre = Column(Uuid, ForeignKey("bdns.organo.id"))
    nivel1 = Column(String)
    nivel1_norm = Column(String)
    nivel2 = Column(String)
    nivel2_norm = Column(String)
    nivel3 = Column(String)
    nivel3_norm = Column(String)
    nombre = Column(String, nullable=False)
    padre = relationship("Organo", remote_side="Organo.id", back_populates="hijos")
    hijos = relationship("Organo", back_populates="padre")
    tipo = Column(String, nullable=False)


class Reglamento(UUIDMixin, Base):
    __tablename__ = "reglamento"
    __table_args__ = {'schema': 'bdns'}

    ambito = Column(String, default="GE")
    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String, nullable=False)
    descripcion_norm = Column(String, index=True)
    autorizacion = Column(Integer)


class Region(UUIDMixin, Base):
    __tablename__ = "region"
    __table_args__ = {'schema': 'bdns'}

    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String, nullable=False)
    descripcion_norm = Column(String, nullable=False, index=True)
    id_padre = Column(Uuid, ForeignKey("bdns.region.id"))
    padre = relationship("Region", remote_side="Region.id", back_populates="hijos")
    hijos = relationship("Region", back_populates="padre")


class RegimenAyuda(UUIDMixin, Base):
    __tablename__ = "regimen_ayuda"
    __table_args__ = {'schema': 'bdns'}

    descripcion = Column(String, nullable=False, unique=True)
    descripcion_norm = Column(String, nullable=False, unique=True, index=True)


class SectorActividad(UUIDMixin, Base):
    __tablename__ = "sector_actividad"
    __table_args__ = {'schema': 'bdns'}

    codigo = Column(String, nullable=False, unique=True, index=True)
    descripcion = Column(String, nullable=False)
    descripcion_norm = Column(String, index=True)
    id_padre = Column(Uuid, ForeignKey("bdns.sector_actividad.id"))
    padre = relationship("SectorActividad", remote_side="SectorActividad.id", back_populates="hijos")
    hijos = relationship("SectorActividad", back_populates="padre")


class SectorProducto(UUIDMixin, Base):
    __tablename__ = "sector_producto"
    __table_args__ = {'schema': 'bdns'}

    api_id = Column(Integer, unique=True, index=True)
    descripcion = Column(String, nullable=False)
    descripcion_norm = Column(String, index=True)


class TipoBeneficiario(UUIDMixin, Base):
    __tablename__ = "tipo_beneficiario"
    __table_args__ = {'schema': 'bdns'}

    api_id = Column(Integer, unique=True, index=True)
    codigo = Column(String, index=True)
    descripcion = Column(String, nullable=False)
    descripcion_norm = Column(String, index=True)


# =========================================================
# TABLAS PUENTE N:M (definidas aquí, antes de Convocatoria)
# =========================================================

convocatoria_instrumento = Table(
    "convocatoria_instrumento",
    Base.metadata,
    Column("convocatoria_id", Uuid, ForeignKey("bdns.convocatoria.id", ondelete="CASCADE"), primary_key=True),
    Column("instrumento_id", Uuid, ForeignKey("bdns.instrumento.id"), primary_key=True),
    schema="bdns"
)

convocatoria_tipo_beneficiario = Table(
    "convocatoria_tipo_beneficiario",
    Base.metadata,
    Column("convocatoria_id", Uuid, ForeignKey("bdns.convocatoria.id", ondelete="CASCADE"), primary_key=True),
    Column("tipo_beneficiario_id", Uuid, ForeignKey("bdns.tipo_beneficiario.id"), primary_key=True),
    schema="bdns"
)

convocatoria_sector_actividad = Table(
    "convocatoria_sector_actividad",
    Base.metadata,
    Column("convocatoria_id", Uuid, ForeignKey("bdns.convocatoria.id", ondelete="CASCADE"), primary_key=True),
    Column("sector_actividad_id", Uuid, ForeignKey("bdns.sector_actividad.id"), primary_key=True),
    schema="bdns"
)

convocatoria_region = Table(
    "convocatoria_region",
    Base.metadata,
    Column("convocatoria_id", Uuid, ForeignKey("bdns.convocatoria.id", ondelete="CASCADE"), primary_key=True),
    Column("region_id", Uuid, ForeignKey("bdns.region.id"), primary_key=True),
    schema="bdns"
)

convocatoria_fondo = Table(
    "convocatoria_fondo",
    Base.metadata,
    Column("convocatoria_id", Uuid, ForeignKey("bdns.convocatoria.id", ondelete="CASCADE"), primary_key=True),
    Column("fondo_id", Uuid, ForeignKey("bdns.fondo.id"), primary_key=True),
    schema="bdns"
)

convocatoria_objetivo = Table(
    "convocatoria_objetivo",
    Base.metadata,
    Column("convocatoria_id", Uuid, ForeignKey("bdns.convocatoria.id", ondelete="CASCADE"), primary_key=True),
    Column("objetivo_id", Uuid, ForeignKey("bdns.objetivo.id"), primary_key=True),
    schema="bdns"
)

convocatoria_sector_producto = Table(
    "convocatoria_sector_producto",
    Base.metadata,
    Column("convocatoria_id", Uuid, ForeignKey("bdns.convocatoria.id", ondelete="CASCADE"), primary_key=True),
    Column("sector_producto_id", Uuid, ForeignKey("bdns.sector_producto.id"), primary_key=True),
    schema="bdns"
)


# =========================================================
# CONVOCATORIA Y ENTIDADES RELACIONADAS
# =========================================================

class Convocatoria(UUIDMixin, Base, AuditMixin):
    __tablename__ = "convocatoria"
    __table_args__ = (
        Index("idx_convocatoria_codigo_bdns", "codigo_bdns", unique=True),
        {'schema': 'bdns'}
    )

    # Clave natural de la API
    codigo_bdns = Column(String, nullable=False, index=True)
    
    # Campos descriptivos
    titulo = Column(String)
    descripcion = Column(Text)
    descripcion_leng = Column(Text)
    
    # Fechas
    fecha_recepcion = Column(Date)
    fecha_inicio_solicitud = Column(Date)
    fecha_fin_solicitud = Column(Date)
    
    # URLs y enlaces
    sede_electronica = Column(String)
    url_bases_reguladoras = Column(String)
    url_ayuda_estado = Column(String)
    
    # Datos numéricos y flags
    presupuesto_total = Column(Float)
    mrr = Column(Boolean, default=False)
    tipo_convocatoria = Column(String)
    descripcion_bases_reguladoras = Column(Text)
    se_publica_diario_oficial = Column(Boolean)
    abierto = Column(Boolean)
    ayuda_estado = Column(String)
    
    # FKs simples a catálogos
    organo_id = Column(Uuid, ForeignKey("bdns.organo.id"))
    reglamento_id = Column(Uuid, ForeignKey("bdns.reglamento.id"))
    finalidad_id = Column(Uuid, ForeignKey("bdns.finalidad.id"))
    
    # Relaciones 1:N
    organo = relationship("Organo")
    reglamento = relationship("Reglamento")
    finalidad = relationship("Finalidad")
    concesiones = relationship("Concesion", back_populates="convocatoria", cascade="all, delete-orphan")

    # Relaciones N:M (referencian las tablas puente definidas arriba)
    instrumentos = relationship("Instrumento", secondary=convocatoria_instrumento)
    tipos_beneficiarios = relationship("TipoBeneficiario", secondary=convocatoria_tipo_beneficiario)
    sectores_actividad = relationship("SectorActividad", secondary=convocatoria_sector_actividad)
    regiones = relationship("Region", secondary=convocatoria_region)
    fondos = relationship("Fondo", secondary=convocatoria_fondo)
    objetivos = relationship("Objetivo", secondary=convocatoria_objetivo)
    sectores_producto = relationship("SectorProducto", secondary=convocatoria_sector_producto)
    
    # Entidades anidadas 1:N
    documentos = relationship("DocumentoConvocatoria", back_populates="convocatoria", cascade="all, delete-orphan")
    anuncios = relationship("AnuncioConvocatoria", back_populates="convocatoria", cascade="all, delete-orphan")


class DocumentoConvocatoria(UUIDMixin, Base):
    __tablename__ = "documento_convocatoria"
    __table_args__ = {'schema': 'bdns'}
    
    convocatoria_id = Column(Uuid, ForeignKey("bdns.convocatoria.id", ondelete="CASCADE"), nullable=False)
    api_id = Column(Integer, index=True)
    nombre_fichero = Column(String)
    descripcion = Column(String)
    longitud = Column(Integer)
    fecha_modificacion = Column(Date)
    fecha_publicacion = Column(Date)
    
    convocatoria = relationship("Convocatoria", back_populates="documentos")


class AnuncioConvocatoria(UUIDMixin, Base):
    __tablename__ = "anuncio_convocatoria"
    __table_args__ = {'schema': 'bdns'}
    
    convocatoria_id = Column(Uuid, ForeignKey("bdns.convocatoria.id", ondelete="CASCADE"), nullable=False)
    num_anuncio = Column(Integer, index=True)
    titulo = Column(Text)
    titulo_leng = Column(Text)
    texto = Column(Text)
    texto_leng = Column(Text)
    url = Column(String)
    cve = Column(String)
    descripcion_diario_oficial = Column(String)
    fecha_publicacion = Column(Date)
    
    convocatoria = relationship("Convocatoria", back_populates="anuncios")


# =========================================================
# USUARIOS Y AUTENTICACIÓN (al final, no depende de nada)
# =========================================================

class Usuario(UUIDMixin, AuditMixin, Base):
    """
    Usuario del sistema BDNS.
    """
    __tablename__ = "usuario"

    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    nombre = Column(String(255))
    role = Column(String(50), nullable=False, default="user", index=True)
    activo = Column(Boolean, nullable=False, default=True, index=True)
    telegram_chat_id = Column(String(50), unique=True, index=True)
    telegram_username = Column(String(100))
    telegram_verificado = Column(Boolean, default=False)

    __table_args__ = (
        Index("idx_usuario_username_activo", "username", "activo"),
        Index("idx_usuario_email_activo", "email", "activo"),
        Index("idx_usuario_role_activo", "role", "activo"),
        {'schema': 'bdns'}
    )

    def __repr__(self):
        return f"<Usuario(username={self.username}, email={self.email}, role={self.role})>"


# ============================= 
# BENEFICIARIOS Y CONCESIONES 
# ============================= 

class Beneficiario(UUIDMixin, Base, AuditMixin):
    __tablename__ = "beneficiario"
    __table_args__ = {'schema': 'bdns'}

    forma_juridica_id = Column(Uuid, ForeignKey("bdns.forma_juridica.id"))
    nif = Column(String, index=True)
    nombre = Column(String, nullable=False)
    nombre_norm = Column(String, nullable=False)
    tipo_beneficiario_id = Column(Uuid, ForeignKey("bdns.tipo_beneficiario.id"))
    forma_juridica = relationship("FormaJuridica")
    tipo_beneficiario = relationship("TipoBeneficiario")
    pseudonimos = relationship("Pseudonimo", back_populates="beneficiario", cascade="all, delete-orphan")

    concesiones = relationship("Concesion", back_populates="beneficiario", cascade="all, delete-orphan")
    
    @property
    def es_entidad_publica(self) -> bool:
        if not self.forma_juridica:
            return False
        return self.forma_juridica.tipo == "publica"

    @property
    def es_persona_fisica(self) -> bool:
        if not self.forma_juridica:
            return False
        return self.forma_juridica.es_persona_fisica

    @property
    def es_persona_juridica(self) -> bool:
        if not self.forma_juridica:
            return False
        return not self.forma_juridica.es_persona_fisica and self.forma_juridica.tipo != "desconocido"


class Pseudonimo(UUIDMixin, Base):
    __tablename__ = "pseudonimo"

    beneficiario_id = Column(Uuid, ForeignKey("bdns.beneficiario.id"), nullable=False)
    pseudonimo = Column(String, nullable=False)
    pseudonimo_norm = Column(String, nullable=False)

    beneficiario = relationship("Beneficiario", back_populates="pseudonimos")

    __table_args__ = (
        UniqueConstraint("beneficiario_id", "pseudonimo_norm", name="uq_beneficiario_pseudonimo"),
        {'schema': 'bdns'}
    )


class Concesion(UUIDMixin, Base, AuditMixin):
    __tablename__ = "concesion"
    __table_args__ = (
        Index("ix_concesion_beneficiario_id", "beneficiario_id"),
        Index("ix_concesion_convocatoria_id", "convocatoria_id"),
        Index("ix_concesion_fecha_concesion", "fecha_concesion"),
        Index("ix_concesion_beneficiario_fecha", "beneficiario_id", "fecha_concesion"),
        Index("ix_concesion_convocatoria_fecha", "convocatoria_id", "fecha_concesion"),
        UniqueConstraint("id_concesion", name="uq_concesion_id_concesion"),
        {'schema': 'bdns'}
    )

    id_concesion = Column(String, nullable=False, unique=True, index=True)
    fecha_concesion = Column(Date, nullable=False, index=True)
    
    beneficiario_id = Column(Uuid, ForeignKey("bdns.beneficiario.id"), nullable=False)
    convocatoria_id = Column(Uuid, ForeignKey("bdns.convocatoria.id"), nullable=False)
    regimen_ayuda_id = Column(Uuid, ForeignKey("bdns.regimen_ayuda.id"))
    
    importe_equivalente = Column(Integer)
    importe_nominal = Column(Integer)
    
    beneficiario = relationship("Beneficiario", back_populates="concesiones")
    convocatoria = relationship("Convocatoria", back_populates="concesiones")
    regimen_ayuda = relationship("RegimenAyuda")

    @property
    def regimen_tipo_norm(self) -> Optional[str]:
        """Ayuda de estado / minimis / ordinaria"""
        if self.regimen_ayuda:
            return self.regimen_ayuda.descripcion_norm
        return None

    @property
    def es_ayuda_estado(self) -> bool:
        return self.regimen_tipo_norm == "ayuda_estado"

    @property
    def es_minimis(self) -> bool:
        return self.regimen_tipo_norm == "minimis"

    @property
    def importe(self) -> int:
        if self.es_ayuda_estado:
            return self.importe_equivalente or 0
        return self.importe_nominal or 0

