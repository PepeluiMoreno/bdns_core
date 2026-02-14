"""
Sistema de logging centralizado para BDNS.

Provee configuración consistente usando settings de bdns_core.config.
"""
import logging
import sys
import json
from datetime import datetime
from functools import lru_cache
from typing import Optional

from bdns_core.config import get_base_settings


class StructuredFormatter(logging.Formatter):
    """JSON formatter para producción."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


class DevelopmentFormatter(logging.Formatter):
    """Formatter coloreado para desarrollo."""
    
    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    FORMATS = {
        logging.DEBUG: grey,
        logging.INFO: blue,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: bold_red,
    }
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.FORMATS.get(record.levelno, self.grey)
        formatter = logging.Formatter(
            f"{color}%(asctime)s - %(name)s - %(levelname)s - %(message)s{self.reset}"
        )
        return formatter.format(record)


@lru_cache()
def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Obtiene logger configurado según settings de bdns_core.
    
    Args:
        name: Nombre del logger (__name__)
        level: Nivel específico (opcional, sobreescribe settings)
    """
    settings = get_base_settings()
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    # Nivel desde settings o parámetro
    if level:
        log_level = getattr(logging, level.upper())
    else:
        log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    logger.setLevel(log_level)
    
    # Handler con formatter según entorno
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    if settings.ENVIRONMENT == "production":
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(DevelopmentFormatter())
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger