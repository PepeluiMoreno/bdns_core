"""
Configuración base compartida por todos los proyectos BDNS.

Contiene settings comunes: base de datos, JWT, logging, etc.
"""
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings as PydanticBaseSettings, SettingsConfigDict


class BaseSettings(PydanticBaseSettings):
    """
    Settings base compartidos por bdns_portal y bdns_etl.

    Carga variables de entorno automáticamente.
    Prioridad: .env.development > .env > defaults
    """

    # ==========================================
    # ENVIRONMENT
    # ==========================================

    ENVIRONMENT: str = Field(
        default="development",
        description="Environment mode: development | production"
    )

    # ==========================================
    # DATABASE
    # ==========================================

    DATABASE_URL: str = Field(
        default="postgresql://bdns_user:password@localhost:5432/bdns",
        description="PostgreSQL database URL"
    )

    # Fallback individual components
    DB_USER_LOCAL: str = "postgres"
    DB_PASSWORD_LOCAL: str = "postgres"
    DB_HOST_LOCAL: str = "localhost"
    DB_PORT_LOCAL: int = 5432
    DB_NAME_LOCAL: str = "bdns"

    # Connection pool
    POOL_SIZE: int = Field(default=20, ge=1, le=100)
    POOL_MAX_OVERFLOW: int = Field(default=10, ge=0, le=50)
    POOL_TIMEOUT: int = Field(default=30, ge=5, le=120)

    SQLALCHEMY_ECHO: bool = Field(
        default=False,
        description="Log all SQL queries"
    )

    # ==========================================
    # JWT AUTHENTICATION
    # ==========================================

    JWT_SECRET_KEY: str = Field(
        default="change-me-in-production",
        description="Secret key for JWT signing (CHANGE IN PRODUCTION!)"
    )

    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )

    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        ge=5,
        le=1440,
        description="Access token expiration in minutes"
    )

    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Refresh token expiration in days"
    )

    # ==========================================
    # LOGGING
    # ==========================================

    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )

    LOG_FORMAT: str = Field(
        default="json",
        description="Log format: json | text"
    )

    # ==========================================
    # VALIDATORS
    # ==========================================

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Valida que el environment sea válido."""
        allowed = ["development", "production", "staging", "test"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT debe ser uno de: {allowed}")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida que el log level sea válido."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"LOG_LEVEL debe ser uno de: {allowed}")
        return v_upper

    @field_validator("LOG_FORMAT")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Valida que el log format sea válido."""
        allowed = ["json", "text"]
        if v not in allowed:
            raise ValueError(f"LOG_FORMAT debe ser uno de: {allowed}")
        return v

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Valida que el JWT secret sea seguro en producción."""
        insecure_defaults = [
            "change-me-in-production",
            "changeme",
            "secret",
            "your-secret-key",
        ]
        if v.lower() in insecure_defaults:
            import warnings
            warnings.warn(
                "JWT_SECRET_KEY usa un valor por defecto inseguro. "
                "CAMBIA esto en producción!"
            )
        if len(v) < 32:
            import warnings
            warnings.warn(
                f"JWT_SECRET_KEY tiene solo {len(v)} caracteres. "
                "Se recomienda al menos 32 caracteres para seguridad."
            )
        return v

    # ==========================================
    # HELPERS
    # ==========================================

    def get_database_url(self, async_mode: bool = False) -> str:
        """
        Obtiene la URL de la base de datos.

        Args:
            async_mode: Si True, retorna URL para asyncpg

        Returns:
            Database URL con el driver apropiado
        """
        url = self.DATABASE_URL

        # Normalizar
        url = url.replace("postgresql+asyncpg://", "postgresql://")
        url = url.replace("postgresql+psycopg2://", "postgresql://")

        # Aplicar driver
        if async_mode:
            url = url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            url = url.replace("postgresql://", "postgresql+psycopg2://")

        return url

    def is_production(self) -> bool:
        """Retorna True si estamos en producción."""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Retorna True si estamos en desarrollo."""
        return self.ENVIRONMENT == "development"

    # ==========================================
    # PYDANTIC CONFIG
    # ==========================================

    model_config = SettingsConfigDict(
        env_file=".env.development" if os.getenv("ENVIRONMENT", "development") == "development" else ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_base_settings() -> BaseSettings:
    """
    Obtiene settings base cacheados.

    El decorador @lru_cache asegura que solo se carga una vez.
    """
    return BaseSettings()
