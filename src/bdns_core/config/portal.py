"""
Configuración específica para BDNS Portal.

Extiende BaseSettings con configuración específica del portal público:
- Redis cache
- GraphQL
- CORS para frontend público
"""
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator

from .base import BaseSettings


class PortalSettings(BaseSettings):
    """
    Settings específicos para bdns_portal.

    Hereda todas las settings de BaseSettings y añade:
    - Configuración de Redis
    - Configuración de GraphQL
    - CORS específico del portal
    """

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
        default=4,
        ge=1,
        le=32,
        description="Número de workers de Uvicorn"
    )

    DEBUG: bool = Field(
        default=False,
        description="Modo debug (solo desarrollo)"
    )

    # ==========================================
    # REDIS CACHE
    # ==========================================

    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL para cache"
    )

    REDIS_CACHE_TTL: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="TTL del cache en segundos (default: 1 hora)"
    )

    REDIS_ENABLED: bool = Field(
        default=True,
        description="Habilitar Redis cache"
    )

    # ==========================================
    # GRAPHQL
    # ==========================================

    GRAPHQL_INTROSPECTION: bool = Field(
        default=True,
        description="Habilitar introspección de GraphQL (deshabilitar en prod)"
    )

    GRAPHQL_PLAYGROUND: bool = Field(
        default=True,
        description="Habilitar GraphQL Playground (deshabilitar en prod)"
    )

    GRAPHQL_DEBUG: bool = Field(
        default=False,
        description="Modo debug de GraphQL"
    )

    # ==========================================
    # CORS
    # ==========================================

    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Orígenes permitidos para CORS (separados por coma)"
    )

    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Permitir credenciales en CORS"
    )

    # ==========================================
    # TELEGRAM NOTIFICATIONS (opcional)
    # ==========================================

    TELEGRAM_BOT_TOKEN: str | None = Field(
        default=None,
        description="Token del bot de Telegram para notificaciones"
    )

    TELEGRAM_ENABLED: bool = Field(
        default=False,
        description="Habilitar notificaciones por Telegram"
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
        # Validar que cada origen sea una URL válida
        origins = [o.strip() for o in v.split(",")]
        for origin in origins:
            if origin != "*" and not (origin.startswith("http://") or origin.startswith("https://")):
                raise ValueError(f"Origen CORS inválido: {origin}. Debe empezar con http:// o https://")
        return v

    # ==========================================
    # HELPERS
    # ==========================================

    def get_cors_origins(self) -> List[str]:
        """Retorna lista de orígenes CORS."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    def is_graphql_public(self) -> bool:
        """Retorna True si GraphQL tiene introspección/playground habilitado."""
        return self.GRAPHQL_INTROSPECTION or self.GRAPHQL_PLAYGROUND


@lru_cache()
def get_portal_settings() -> PortalSettings:
    """
    Obtiene settings del portal cacheados.

    Uso:
        from bdns_core.config import get_portal_settings

        settings = get_portal_settings()
        app.add_middleware(CORSMiddleware, allow_origins=settings.get_cors_origins())
    """
    return PortalSettings()
