#src/bdns_core/db/bootstrap/bootstrap.py

"""Módulo para ejecutar scripts SQL de bootstrap """

import logging
from pathlib import Path
from sqlalchemy import text
from bdns_core.db.session import engine

logger = logging.getLogger(__name__)


async def run_sql_file(conn, filepath: Path) -> None:
    """Ejecuta un archivo SQL."""
    with open(filepath, 'r') as f:
        sql = f.read()
    
    for statement in sql.split(';'):
        stmt = statement.strip()
        if stmt:
            await conn.execute(text(stmt))


async def run_bootstrap(bootstrap_dir: Path) -> None:
    """Ejecuta todos los scripts bootstrap en orden."""
    scripts = [
        "01_extensions.sql",
        "02_schemas.sql",
        "03_partition_functions.sql"
    ]
    
    async with engine.begin() as conn:
        for script in scripts:
            path = bootstrap_dir / script
            if path.exists():
                logger.info(f"Ejecutando {script}")
                await run_sql_file(conn, path)
            else:
                logger.warning(f"{script} no encontrado, ignorando")


async def bootstrap_if_needed() -> bool:
    """Ejecuta bootstrap SOLO si es necesario."""
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = 'bdns')")
        )
        exists = result.scalar()
        
        if not exists:
            logger.info("Esquema bdns no encontrado, ejecutando bootstrap")
            bootstrap_dir = Path(__file__).parent / "bootstrap"
            await run_bootstrap(bootstrap_dir)
            return True
        
        logger.debug("Esquema bdns ya existe, bootstrap omitido")
        return False