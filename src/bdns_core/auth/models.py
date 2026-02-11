"""
Schemas Pydantic para autenticación y gestión de usuarios.

Estos modelos se usan para validación de datos y serialización
en las APIs de bdns_portal y bdns_etl.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# ==========================================
# SCHEMAS DE USUARIO
# ==========================================

class UsuarioBase(BaseModel):
    """Schema base de usuario (campos comunes)."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    nombre: Optional[str] = Field(None, max_length=255)
    role: str = Field(default="user", pattern="^(admin|user|viewer)$")
    activo: bool = True

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Valida que el username sea alfanumérico."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username solo puede contener letras, números, guiones y guiones bajos")
        return v.lower()


class UsuarioCreate(BaseModel):
    """Schema para crear un usuario nuevo."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    nombre: Optional[str] = Field(None, max_length=255)
    role: str = Field(default="user", pattern="^(admin|user|viewer)$")
    activo: bool = True

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Valida que el username sea alfanumérico."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username solo puede contener letras, números, guiones y guiones bajos")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Valida que el password sea seguro."""
        if len(v) < 8:
            raise ValueError("Password debe tener al menos 8 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("Password debe contener al menos una mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("Password debe contener al menos una minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password debe contener al menos un número")
        return v


class UsuarioUpdate(BaseModel):
    """Schema para actualizar un usuario existente."""
    email: Optional[EmailStr] = None
    nombre: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field(None, pattern="^(admin|user|viewer)$")
    activo: Optional[bool] = None
    telegram_chat_id: Optional[str] = Field(None, max_length=50)
    telegram_username: Optional[str] = Field(None, max_length=100)
    telegram_verificado: Optional[bool] = None


class UsuarioChangePassword(BaseModel):
    """Schema para cambiar password de usuario."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Valida que el password sea seguro."""
        if len(v) < 8:
            raise ValueError("Password debe tener al menos 8 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("Password debe contener al menos una mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("Password debe contener al menos una minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password debe contener al menos un número")
        return v


class UsuarioResponse(BaseModel):
    """Schema de respuesta de usuario (sin password)."""
    id: str
    username: str
    email: str
    nombre: Optional[str] = None
    role: str
    activo: bool
    telegram_chat_id: Optional[str] = None
    telegram_username: Optional[str] = None
    telegram_verificado: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UsuarioInDB(UsuarioBase):
    """Schema de usuario en base de datos (con password hash)."""
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ==========================================
# SCHEMAS DE AUTENTICACIÓN
# ==========================================

class LoginRequest(BaseModel):
    """Request de login."""
    username: str
    password: str


class Token(BaseModel):
    """Response de autenticación con tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Request para renovar access token."""
    refresh_token: str


class UserInToken(BaseModel):
    """Usuario extraído del token JWT."""
    username: str
    role: str


class TokenData(BaseModel):
    """Datos contenidos en el token JWT."""
    username: str
    role: str = "user"
    exp: Optional[datetime] = None
