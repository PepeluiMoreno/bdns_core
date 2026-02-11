"""
Sistema de configuración centralizado para BDNS.

Este módulo proporciona configuración basada en Pydantic Settings
que puede ser compartida entre bdns_portal y bdns_etl.

Uso:
    from bdns_core.config import get_portal_settings, get_etl_settings

    settings = get_portal_settings()
    print(settings.DATABASE_URL)
"""
from .base import BaseSettings, get_base_settings
from .portal import PortalSettings, get_portal_settings
from .etl import ETLSettings, get_etl_settings

__all__ = [
    "BaseSettings",
    "PortalSettings",
    "ETLSettings",
    "get_base_settings",
    "get_portal_settings",
    "get_etl_settings",
]
