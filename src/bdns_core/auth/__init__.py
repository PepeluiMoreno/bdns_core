"""
Módulo de autenticación compartido.

Exporta todo lo necesario para autenticación y gestión de usuarios:
- JWT: Creación y validación de tokens
- Password: Hashing y verificación
- Models: Schemas Pydantic
- Service: CRUD de usuarios
- Dependencies: FastAPI dependencies
- Secrets: Gestión de credenciales
"""

# JWT Auth
from .jwt_auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
    create_token_pair,
    refresh_access_token,
)

# Models (Schemas Pydantic)
from .models import (
    UsuarioBase,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioChangePassword,
    UsuarioResponse,
    UsuarioInDB,
    LoginRequest,
    Token,
    TokenRefresh,
    UserInToken,
    TokenData,
)

# Alias para compatibilidad
UserResponse = UsuarioResponse

# Service (CRUD)
from .service import UserService

# Dependencies (FastAPI)
from .dependencies import (
    get_current_user,
    require_role,
    require_admin,
    require_user,
    require_viewer,
    get_optional_user,
    CurrentUser,
    AdminUser,
    RegularUser,
    OptionalUser,
)

# Secrets Manager
from .secrets import SecretsManager, get_secrets_manager, secrets_manager

__all__ = [
    # Password
    "verify_password",
    "get_password_hash",
    # JWT
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_token",
    "create_token_pair",
    "refresh_access_token",
    # Models
    "UsuarioBase",
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioChangePassword",
    "UsuarioResponse",
    "UserResponse",  # Alias
    "UsuarioInDB",
    "LoginRequest",
    "Token",
    "TokenRefresh",
    "UserInToken",
    "TokenData",
    # Service
    "UserService",
    # Dependencies
    "get_current_user",
    "require_role",
    "require_admin",
    "require_user",
    "require_viewer",
    "get_optional_user",
    "CurrentUser",
    "AdminUser",
    "RegularUser",
    "OptionalUser",
    # Secrets
    "SecretsManager",
    "get_secrets_manager",
    "secrets_manager",
]
