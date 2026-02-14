# BDNS Core - Bootstrap SQL

Este directorio contiene scripts SQL de **UNA SOLA EJECUCIÓN** para inicializar infraestructura de base de datos.

## Orden de ejecución:
1. `01_extensions.sql` - Extensiones PostgreSQL (uuid-ossp, etc)
2. `02_schemas.sql` - Creación de esquemas (bdns)
3. `03_partition_functions.sql` - Funciones PL/pgSQL para particionado dinámico

## ⚠️ IMPORTANTE
Estos scripts se ejecutan UNA VEZ al crear la base de datos.
NO se versionan con Alembic. NO se hace rollback.

Para cambios en estos scripts, crear NUEVA migración.