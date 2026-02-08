"""
Sistema de autenticación JWT compartido.

Este módulo proporciona autenticación JWT que puede ser usada
por ambos backends (bdns-search y etl-admin).

Características:
- JWT tokens con expiración
- Refresh tokens
- Roles de usuario (admin, user)
- Password hashing con bcrypt
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


# Configuración JWT
# IMPORTANTE: En producción, usar variables de entorno
SECRET_KEY = "tu-clave-secreta-muy-segura-cambiar-en-produccion"  # TODO: Mover a .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# Contexto de hashing de passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==========================================
# SCHEMAS
# ==========================================

class TokenData(BaseModel):
    """Datos contenidos en el token JWT."""
    username: str
    role: str = "user"
    exp: Optional[datetime] = None


class Token(BaseModel):
    """Response de autenticación."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserInToken(BaseModel):
    """Usuario extraído del token."""
    username: str
    role: str


# ==========================================
# FUNCIONES DE PASSWORD
# ==========================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que el password en texto plano coincida con el hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera hash de un password."""
    return pwd_context.hash(password)


# ==========================================
# FUNCIONES JWT
# ==========================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT access token.

    Args:
        data: Datos a incluir en el token (ej: username, role)
        expires_delta: Tiempo de expiración (default: 30 min)

    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Crea un JWT refresh token (larga duración).

    Args:
        data: Datos a incluir en el token

    Returns:
        Refresh token JWT
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica y valida un JWT token.

    Args:
        token: Token JWT a decodificar

    Returns:
        Payload del token o None si es inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Optional[UserInToken]:
    """
    Verifica un token JWT y extrae el usuario.

    Args:
        token: Token JWT

    Returns:
        UserInToken si es válido, None si no
    """
    payload = decode_token(token)
    if payload is None:
        return None

    username = payload.get("sub")
    role = payload.get("role", "user")

    if username is None:
        return None

    return UserInToken(username=username, role=role)


# ==========================================
# HELPERS
# ==========================================

def create_token_pair(username: str, role: str = "user") -> Token:
    """
    Crea un par de tokens (access + refresh).

    Args:
        username: Nombre de usuario
        role: Rol del usuario (admin, user)

    Returns:
        Token con access_token y refresh_token
    """
    access_token = create_access_token(
        data={"sub": username, "role": role}
    )
    refresh_token = create_refresh_token(
        data={"sub": username, "role": role}
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Genera un nuevo access token a partir de un refresh token válido.

    Args:
        refresh_token: Refresh token JWT

    Returns:
        Nuevo access token o None si el refresh token es inválido
    """
    payload = decode_token(refresh_token)
    if payload is None:
        return None

    # Verificar que sea un refresh token
    if payload.get("type") != "refresh":
        return None

    username = payload.get("sub")
    role = payload.get("role", "user")

    if username is None:
        return None

    # Crear nuevo access token
    return create_access_token(data={"sub": username, "role": role})
