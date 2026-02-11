"""
Servicio de gestión de usuarios para BDNS.

Proporciona CRUD completo de usuarios y funciones de autenticación.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from bdns_core.db.models import Usuario
from bdns_core.auth.jwt_auth import get_password_hash, verify_password
from bdns_core.auth.models import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    UsuarioChangePassword,
)


class UserService:
    """Servicio para gestión de usuarios."""

    # ==========================================
    # CRUD BÁSICO
    # ==========================================

    @staticmethod
    def create_user(db: Session, user_data: UsuarioCreate) -> Usuario:
        """
        Crea un nuevo usuario.

        Args:
            db: Sesión de base de datos
            user_data: Datos del usuario a crear

        Returns:
            Usuario creado

        Raises:
            IntegrityError: Si username o email ya existen
        """
        # Hash del password
        hashed_password = get_password_hash(user_data.password)

        # Crear usuario
        db_user = Usuario(
            username=user_data.username.lower(),
            email=user_data.email.lower(),
            hashed_password=hashed_password,
            nombre=user_data.nombre,
            role=user_data.role,
            activo=user_data.activo,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[Usuario]:
        """Obtiene un usuario por ID."""
        return db.query(Usuario).filter(Usuario.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[Usuario]:
        """Obtiene un usuario por username."""
        return db.query(Usuario).filter(Usuario.username == username.lower()).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[Usuario]:
        """Obtiene un usuario por email."""
        return db.query(Usuario).filter(Usuario.email == email.lower()).first()

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        activo: Optional[bool] = None,
        role: Optional[str] = None,
    ) -> List[Usuario]:
        """
        Lista usuarios con filtros opcionales.

        Args:
            db: Sesión de base de datos
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            activo: Filtrar por estado activo/inactivo
            role: Filtrar por rol

        Returns:
            Lista de usuarios
        """
        query = db.query(Usuario)

        if activo is not None:
            query = query.filter(Usuario.activo == activo)

        if role is not None:
            query = query.filter(Usuario.role == role)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_user(
        db: Session,
        user_id: str,
        user_data: UsuarioUpdate,
    ) -> Optional[Usuario]:
        """
        Actualiza un usuario existente.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario a actualizar
            user_data: Datos a actualizar

        Returns:
            Usuario actualizado o None si no existe
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        # Actualizar solo campos que no son None
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """
        Elimina un usuario (soft delete: marca como inactivo).

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario a eliminar

        Returns:
            True si se eliminó, False si no existe
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False

        db_user.activo = False
        db.commit()

        return True

    @staticmethod
    def hard_delete_user(db: Session, user_id: str) -> bool:
        """
        Elimina permanentemente un usuario de la base de datos.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario a eliminar

        Returns:
            True si se eliminó, False si no existe
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()

        return True

    # ==========================================
    # AUTENTICACIÓN
    # ==========================================

    @staticmethod
    def authenticate_user(
        db: Session,
        username: str,
        password: str,
    ) -> Optional[Usuario]:
        """
        Autentica un usuario con username y password.

        Args:
            db: Sesión de base de datos
            username: Username del usuario
            password: Password en texto plano

        Returns:
            Usuario si las credenciales son válidas, None si no
        """
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None

        if not user.activo:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def change_password(
        db: Session,
        user_id: str,
        password_data: UsuarioChangePassword,
    ) -> bool:
        """
        Cambia el password de un usuario.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            password_data: Datos de cambio de password

        Returns:
            True si se cambió, False si las credenciales son inválidas
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        # Verificar password actual
        if not verify_password(password_data.current_password, user.hashed_password):
            return False

        # Actualizar password
        user.hashed_password = get_password_hash(password_data.new_password)
        db.commit()

        return True

    @staticmethod
    def reset_password(
        db: Session,
        user_id: str,
        new_password: str,
    ) -> bool:
        """
        Resetea el password de un usuario (admin only).

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            new_password: Nuevo password en texto plano

        Returns:
            True si se cambió, False si el usuario no existe
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        user.hashed_password = get_password_hash(new_password)
        db.commit()

        return True

    # ==========================================
    # TELEGRAM
    # ==========================================

    @staticmethod
    def link_telegram(
        db: Session,
        user_id: str,
        telegram_chat_id: str,
        telegram_username: Optional[str] = None,
    ) -> Optional[Usuario]:
        """
        Vincula un usuario con una cuenta de Telegram.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            telegram_chat_id: Chat ID de Telegram
            telegram_username: Username de Telegram (opcional)

        Returns:
            Usuario actualizado o None si no existe
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        user.telegram_chat_id = telegram_chat_id
        user.telegram_username = telegram_username
        user.telegram_verificado = True

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def unlink_telegram(db: Session, user_id: str) -> Optional[Usuario]:
        """
        Desvincula un usuario de Telegram.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario

        Returns:
            Usuario actualizado o None si no existe
        """
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        user.telegram_chat_id = None
        user.telegram_username = None
        user.telegram_verificado = False

        db.commit()
        db.refresh(user)

        return user

    # ==========================================
    # UTILIDADES
    # ==========================================

    @staticmethod
    def count_users(db: Session, activo: Optional[bool] = None) -> int:
        """
        Cuenta el número de usuarios.

        Args:
            db: Sesión de base de datos
            activo: Filtrar por estado activo/inactivo

        Returns:
            Número de usuarios
        """
        query = db.query(Usuario)

        if activo is not None:
            query = query.filter(Usuario.activo == activo)

        return query.count()

    @staticmethod
    def user_exists(db: Session, username: str) -> bool:
        """Verifica si un usuario existe por username."""
        return UserService.get_user_by_username(db, username) is not None

    @staticmethod
    def email_exists(db: Session, email: str) -> bool:
        """Verifica si un email ya está registrado."""
        return UserService.get_user_by_email(db, email) is not None
