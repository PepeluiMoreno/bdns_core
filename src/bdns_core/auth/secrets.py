"""
Servicio para leer credenciales desde Docker secrets.

En Docker Compose, los secrets se montan en /run/secrets/
En desarrollo local, se leen desde variables de entorno.

Este módulo se mueve desde bdns_etl a bdns_core para ser
compartido entre proyectos.
"""
import os
from pathlib import Path
from typing import Optional

from bdns_core.config import get_etl_settings


class SecretsManager:
    """Gestor de secrets para credenciales de autenticación."""

    def __init__(self, secrets_dir: Optional[str] = None):
        """
        Inicializa el gestor de secrets.

        Args:
            secrets_dir: Directorio de secrets (default: /run/secrets o desde config)
        """
        if secrets_dir:
            self.secrets_dir = Path(secrets_dir)
        else:
            # Intentar leer desde config ETL
            try:
                settings = get_etl_settings()
                self.secrets_dir = Path(settings.SECRETS_DIR)
            except Exception:
                # Fallback a default
                self.secrets_dir = Path("/run/secrets")

    def read_secret(self, secret_name: str) -> Optional[str]:
        """
        Lee un secret desde Docker o variable de entorno.

        Prioridad:
        1. Docker secret en /run/secrets/{secret_name}
        2. Variable de entorno {secret_name.upper()}
        3. None si no existe

        Args:
            secret_name: Nombre del secret (ej: "admin_username")

        Returns:
            Contenido del secret o None
        """
        # Intentar leer desde Docker secret
        secret_path = self.secrets_dir / secret_name
        if secret_path.exists() and secret_path.is_file():
            try:
                return secret_path.read_text().strip()
            except Exception:
                pass

        # Fallback: variable de entorno
        env_var = secret_name.upper()
        return os.getenv(env_var)

    def get_admin_credentials(self) -> tuple[str, str]:
        """
        Obtiene credenciales de administrador.

        Returns:
            (username, hashed_password) tupla

        Raises:
            ValueError: Si no se encuentran las credenciales
        """
        username = self.read_secret("admin_username")
        password_hash = self.read_secret("admin_password_hash")

        if not username or not password_hash:
            raise ValueError(
                "Credenciales de admin no configuradas. "
                "Configura admin_username y admin_password_hash en Docker secrets "
                "o variables de entorno (ADMIN_USERNAME, ADMIN_PASSWORD_HASH)."
            )

        return username, password_hash

    def get_user_credentials(self) -> Optional[tuple[str, str]]:
        """
        Obtiene credenciales de usuario normal (opcional).

        Returns:
            (username, hashed_password) tupla o None si no está configurado
        """
        username = self.read_secret("user_username")
        password_hash = self.read_secret("user_password_hash")

        if username and password_hash:
            return username, password_hash

        return None

    def has_secrets(self) -> bool:
        """
        Verifica si hay secrets configurados.

        Returns:
            True si el directorio de secrets existe y es accesible
        """
        return self.secrets_dir.exists() and self.secrets_dir.is_dir()

    def list_secrets(self) -> list[str]:
        """
        Lista todos los secrets disponibles.

        Returns:
            Lista de nombres de secrets
        """
        if not self.has_secrets():
            return []

        try:
            return [f.name for f in self.secrets_dir.iterdir() if f.is_file()]
        except Exception:
            return []


# Singleton global
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager(secrets_dir: Optional[str] = None) -> SecretsManager:
    """
    Obtiene la instancia singleton del SecretsManager.

    Args:
        secrets_dir: Directorio de secrets (solo se usa en primera llamada)

    Returns:
        SecretsManager singleton
    """
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager(secrets_dir)
    return _secrets_manager


# Alias para compatibilidad
secrets_manager = get_secrets_manager()
