"""
Configuración específica para BDNS ETL Admin.

Extiende BaseSettings con configuración específica del sistema ETL:
- API BDNS oficial
- CORS para frontend admin
- Configuración de procesos ETL
"""
from functools import lru_cache
from typing import List

from pydantic import Field, HttpUrl, field_validator

from .base import BaseSettings


class ETLSettings(BaseSettings):
    """
    Settings específicos para bdns_etl.

    Hereda todas las settings de BaseSettings y añade:
    - Configuración de API BDNS oficial
    - CORS específico del admin
    - Configuración de procesos ETL
    """

    # ==========================================
    # DATABASE (override con usuario bdns_etl)
    # ==========================================

    DATABASE_URL: str = Field(
        default="postgresql://bdns_etl:bdns_etl_password@127.0.0.1:5432/bdns",
        description="PostgreSQL database URL (para usuario ETL)",
        validation_alias="ETL_DATABASE_URL"  # Lee de ETL_DATABASE_URL en .env
    )

    # ==========================================
    # SERVER
    # ==========================================

    HOST: str = Field(
        default="0.0.0.0",
        description="Host del servidor"
    )

    PORT: int = Field(
        default=8001,
        ge=1024,
        le=65535,
        description="Puerto del servidor"
    )

    WORKERS: int = Field(
        default=2,
        ge=1,
        le=16,
        description="Número de workers de Uvicorn"
    )

    DEBUG: bool = Field(
        default=False,
        description="Modo debug (solo desarrollo)"
    )

    # ==========================================
    # CORS
    # ==========================================

    CORS_ORIGINS: str = Field(
        default="http://localhost:3001,http://localhost:5174",
        description="Orígenes permitidos para CORS (separados por coma)"
    )

    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Permitir credenciales en CORS"
    )

    # ==========================================
    # API BDNS OFICIAL
    # ==========================================

    BDNS_API_URL: str = Field(
        default="https://www.infosubvenciones.es/bdnstrans/api",
        description="URL de la API oficial de BDNS"
    )

    BDNS_API_TIMEOUT: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Timeout para requests a la API BDNS (segundos)"
    )

    BDNS_API_RATE_LIMIT: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Límite de requests por segundo a la API BDNS"
    )

    BDNS_API_RETRY_ATTEMPTS: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Número de reintentos en caso de error"
    )

    # ==========================================
    # ETL CONFIGURATION
    # ==========================================

    ETL_BATCH_SIZE: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Tamaño de lote para procesos ETL"
    )

    ETL_MAX_WORKERS: int = Field(
        default=4,
        ge=1,
        le=16,
        description="Número máximo de workers para procesamiento paralelo"
    )

    ETL_TEMP_DIR: str = Field(
        default="/tmp/bdns_etl",
        description="Directorio temporal para archivos ETL"
    )

    SYNC_DIAS_TRAS_CIERRE: int = Field(
        default=720,
        ge=0,
        le=3650,
        description="Días tras cierre para excluir convocatorias de sincronización (720 = 2 años)"
    )

    # ==========================================
    # DOCKER SECRETS (para usuarios admin/user)
    # ==========================================

    SECRETS_DIR: str = Field(
        default="/run/secrets",
        description="Directorio de Docker secrets"
    )

    ADMIN_USERNAME: str | None = Field(
        default=None,
        description="Username del admin (fallback si no hay secret)"
    )

    ADMIN_PASSWORD_HASH: str | None = Field(
        default=None,
        description="Password hash del admin (fallback si no hay secret)"
    )

    USER_USERNAME: str | None = Field(
        default=None,
        description="Username del user (fallback si no hay secret)"
    )

    USER_PASSWORD_HASH: str | None = Field(
        default=None,
        description="Password hash del user (fallback si no hay secret)"
    )

    # ==========================================
    # WEBSOCKET
    # ==========================================

    WS_HEARTBEAT_INTERVAL: int = Field(
        default=30,
        ge=10,
        le=300,
        description="Intervalo de heartbeat para WebSocket (segundos)"
    )

    WS_MAX_CONNECTIONS: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Número máximo de conexiones WebSocket concurrentes"
    )

    # ==========================================
    # AUTO-RESYNC CONFIGURATION
    # ==========================================

    AUTO_RESYNC_ENABLED: bool = Field(
        default=True,
        description="Habilitar resincronización automática cuando se detectan cambios"
    )

    AUTO_RESYNC_MAX_NEW_RECORDS: int = Field(
        default=100,
        ge=0,
        le=100000,
        description="Máximo de registros nuevos para auto-resync. Si se supera, requiere confirmación manual"
    )

    AUTO_RESYNC_MAX_UPDATED_RECORDS: int = Field(
        default=50,
        ge=0,
        le=100000,
        description="Máximo de registros actualizados para auto-resync. Si se supera, requiere confirmación manual"
    )

    # ==========================================
    # VALIDATORS
    # ==========================================

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: str) -> str:
        """Valida que CORS_ORIGINS sea una lista válida."""
        if not v.strip():
            raise ValueError("CORS_ORIGINS no puede estar vacío")
        origins = [o.strip() for o in v.split(",")]
        for origin in origins:
            if origin != "*" and not (origin.startswith("http://") or origin.startswith("https://")):
                raise ValueError(f"Origen CORS inválido: {origin}")
        return v

    @field_validator("BDNS_API_URL")
    @classmethod
    def validate_bdns_api_url(cls, v: str) -> str:
        """Valida que BDNS_API_URL sea una URL válida."""
        if not v.startswith("http://") and not v.startswith("https://"):
            raise ValueError("BDNS_API_URL debe empezar con http:// o https://")
        return v

    # ==========================================
    # HELPERS
    # ==========================================

    def get_cors_origins(self) -> List[str]:
        """Retorna lista de orígenes CORS."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    def has_docker_secrets(self) -> bool:
        """Verifica si hay Docker secrets configurados."""
        import os
        secrets_dir = self.SECRETS_DIR
        required_secrets = ["admin_username", "admin_password_hash"]
        return all(
            os.path.exists(os.path.join(secrets_dir, secret))
            for secret in required_secrets
        )


@lru_cache()
def get_etl_settings() -> ETLSettings:
    """
    Obtiene settings del ETL cacheados.

    Uso:
        from bdns_core.config import get_etl_settings

        settings = get_etl_settings()
        app.add_middleware(CORSMiddleware, allow_origins=settings.get_cors_origins())
    """
    return ETLSettings()
