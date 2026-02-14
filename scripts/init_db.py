#!/usr/bin/env python3
"""Script manual para inicializar base de datos en desarrollo."""

import asyncio
import os
import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bdns_core.db.session import engine
from bdns_core.db.bootstrap import run_bootstrap


async def main():
    """Ejecuta bootstrap completo."""
    print("🚀 Inicializando base de datos BDNS (desarrollo)...")
    
    async with engine.begin() as conn:
        bootstrap_dir = Path(__file__).parent.parent / "src" / "bdns_core" / "db" / "bootstrap"
        await run_bootstrap(conn, bootstrap_dir)
    
    print("✅ Bootstrap completado")
    print("📊 Base de datos lista")


if __name__ == "__main__":
    asyncio.run(main())