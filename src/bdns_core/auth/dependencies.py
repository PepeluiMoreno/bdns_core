"""
Dependencies de FastAPI para autenticación.

Proporciona dependencies reutilizables para proteger endpoints
con autenticación JWT y control de roles.
"""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from bdns_core.auth.jwt_auth import verify_token
from bdns_core.auth.models import UserInToken
from bdns_core.db.session import get_db


# Security scheme para FastAPI
security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> UserInToken:
    """
    Dependency para obtener el usuario actual desde el token JWT.

    Valida el token y verifica que el usuario existe en la base de datos.

    Args:
        credentials: Credenciales HTTP Bearer (token JWT)
        db: Sesión de base de datos

    Returns:
        UserInToken con username y role

    Raises:
        HTTPException 401: Si el token es inválido o el usuario no existe

    Uso:
        @app.get("/protected")
        def protected_route(current_user: UserInToken = Depends(get_current_user)):
            return {"username": current_user.username}
    """
    token = credentials.credentials

    # Verificar y decodificar token
    user = verify_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que el usuario existe y está activo
    from bdns_core.auth.service import UserService
    db_user = UserService.get_user_by_username(db, user.username)

    if not db_user or not db_user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_role(*allowed_roles: str):
    """
    Factory de dependency para requerir roles específicos.

    Args:
        *allowed_roles: Roles permitidos (ej: "admin", "user")

    Returns:
        Dependency function que verifica el rol

    Uso:
        @app.post("/admin/action")
        def admin_action(user: UserInToken = Depends(require_role("admin"))):
            return {"message": "Admin action"}

        @app.get("/content")
        def view_content(user: UserInToken = Depends(require_role("admin", "user"))):
            return {"message": "Content"}
    """
    def role_checker(current_user: Annotated[UserInToken, Depends(get_current_user)]) -> UserInToken:
        """Verifica que el usuario tenga uno de los roles permitidos."""
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere rol: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


# Aliases comunes para facilitar el uso
require_admin = require_role("admin")
require_user = require_role("admin", "user")
require_viewer = require_role("admin", "user", "viewer")


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
) -> UserInToken | None:
    """
    Dependency para obtener el usuario actual si está autenticado (opcional).

    Similar a get_current_user pero no lanza error si no hay token.
    Útil para endpoints públicos que pueden personalizar respuesta si hay usuario.

    Args:
        credentials: Credenciales HTTP Bearer (opcional)
        db: Sesión de base de datos

    Returns:
        UserInToken si hay token válido, None si no

    Uso:
        @app.get("/public")
        def public_route(user: UserInToken | None = Depends(get_optional_user)):
            if user:
                return {"message": f"Hola {user.username}"}
            return {"message": "Hola invitado"}
    """
    if credentials is None:
        return None

    token = credentials.credentials
    user = verify_token(token)

    if user is None:
        return None

    # Verificar que el usuario existe y está activo
    from bdns_core.auth.service import UserService
    db_user = UserService.get_user_by_username(db, user.username)

    if not db_user or not db_user.activo:
        return None

    return user


# Type aliases para facilitar anotaciones
CurrentUser = Annotated[UserInToken, Depends(get_current_user)]
AdminUser = Annotated[UserInToken, Depends(require_admin)]
RegularUser = Annotated[UserInToken, Depends(require_user)]
OptionalUser = Annotated[UserInToken | None, Depends(get_optional_user)]
