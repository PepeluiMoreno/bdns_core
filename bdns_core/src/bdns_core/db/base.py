# bdns_core/db/base.py

from sqlalchemy.orm import DeclarativeBase

# Registrar uuid_utils.UUID para que psycopg2 sepa serializarlo
import psycopg2.extensions
from uuid_utils import UUID as _UUID7
psycopg2.extensions.register_adapter(
    _UUID7,
    lambda u: psycopg2.extensions.AsIs(f"'{u}'"),
)


class Base(DeclarativeBase):
    pass




