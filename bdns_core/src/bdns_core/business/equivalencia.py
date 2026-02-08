"""
Módulo de cálculo de equivalencia de subvenciones (ESG - Equivalent Subsidy Grant).

CONTEXTO LEGAL
==============
El cálculo del importe equivalente de una ayuda pública debe seguir las reglas
establecidas en la normativa europea y española:

NORMATIVA EUROPEA:
- Reglamento (UE) 2023/2831 - De minimis general (2024-2030)
- Reglamento (UE) 651/2014 - Reglamento General de Exención por Categorías (RGEC)
- Comunicación de la Comisión sobre ayudas de Estado (2022/C 485/01)
- Metodología de cálculo del elemento de ayuda en garantías y préstamos

NORMATIVA ESPAÑOLA:
- Ley 38/2003 General de Subvenciones
- Real Decreto 887/2006 - Reglamento de la Ley General de Subvenciones
- Orden EHA/2899/2011 - Transparencia de ayudas públicas

CONCEPTOS CLAVE
===============
1. IMPORTE NOMINAL: Cantidad concedida según acto administrativo
2. IMPORTE EQUIVALENTE (ESG): Ventaja económica efectiva para el beneficiario

TIPOS DE INSTRUMENTOS Y SU CÁLCULO:
------------------------------------
- Subvención directa: 100% del importe nominal
- Préstamo preferente: Diferencia entre interés de mercado e interés aplicado (VAN)
- Garantía: Prima de riesgo que se habría pagado en el mercado
- Aportación de capital: Diferencia respecto a inversión privada en condiciones de mercado
- Ventaja fiscal: Reducción/exención fiscal efectiva
- Otros instrumentos: Según metodología específica

PARÁMETROS DE CÁLCULO:
-----------------------
- Año de concesión (determina reglamento aplicable)
- Régimen de ayuda (de minimis, RGEC, ayuda de estado notificada, ordinaria)
- Instrumento financiero utilizado
- Sector de actividad (algunos sectores tienen reglas específicas)
- Tipo de referencia (Euribor, IRS) para préstamos
- Rating crediticio del beneficiario (para garantías)

TODO: IMPLEMENTACIÓN PENDIENTE
===============================
1. Consultar tablas oficiales de tipos de referencia por año
2. Implementar cálculo VAN para préstamos (tasa de descuento según BCE)
3. Implementar cálculo de primas de garantía según riesgo
4. Validar con casos reales de la BDNS
5. Integrar con tabla de configuración de parámetros

REFERENCIAS:
============
- https://competition-policy.ec.europa.eu/state-aid/legislation/modernisation/gber_en
- https://www.pap.hacienda.gob.es/bdnstrans (Base de Datos Nacional de Subvenciones)
"""

from decimal import Decimal
from datetime import date
from typing import Optional, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TipoInstrumento(str, Enum):
    """Tipos de instrumentos financieros según normativa UE."""
    SUBVENCION_DIRECTA = "subvencion_directa"
    PRESTAMO = "prestamo"
    GARANTIA = "garantia"
    CAPITAL = "capital"
    VENTAJA_FISCAL = "ventaja_fiscal"
    OTRO = "otro"


class RegimenAyuda(str, Enum):
    """Regímenes de ayuda según intensidad de control."""
    DE_MINIMIS = "minimis"
    RGEC = "ayuda de estado"  # Reglamento General de Exención por Categorías
    NOTIFICADA = "notificada"  # Ayuda notificada a la Comisión Europea
    ORDINARIA = "ordinaria"  # No constituye ayuda de estado


def calcular_importe_equivalente(
    importe_nominal: float,
    fecha_concesion: date,
    regimen_ayuda: Optional[str] = None,
    instrumento: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calcula el importe equivalente (ESG) de una concesión.

    IMPLEMENTACIÓN ACTUAL: PLACEHOLDER
    ===================================
    Esta función actualmente usa reglas simplificadas. Se debe reemplazar
    con la lógica completa basada en la normativa vigente.

    Args:
        importe_nominal: Importe nominal de la concesión (€)
        fecha_concesion: Fecha de concesión
        regimen_ayuda: Régimen de ayuda ("minimis", "ayuda de estado", etc.)
        instrumento: Tipo de instrumento financiero
        metadata: Datos adicionales para cálculos específicos
            - plazo_meses: Para préstamos
            - tipo_interes: Para préstamos (%)
            - porcentaje_garantia: Para garantías (%)
            - rating: Rating crediticio (AAA, AA, A, BBB, etc.)

    Returns:
        float: Importe equivalente en euros

    Examples:
        >>> # Subvención directa (caso más común)
        >>> calcular_importe_equivalente(10000.0, date(2023, 1, 1))
        10000.0

        >>> # Préstamo (placeholder simplificado)
        >>> calcular_importe_equivalente(
        ...     100000.0,
        ...     date(2023, 1, 1),
        ...     instrumento="prestamo",
        ...     metadata={"plazo_meses": 60, "tipo_interes": 0.5}
        ... )
        15000.0  # Aproximado

    TODO:
        - Implementar cálculo VAN para préstamos según BCE
        - Implementar primas de garantía según rating
        - Consultar tipos de referencia históricos
        - Validar contra casos reales BDNS
    """
    if importe_nominal is None or importe_nominal == 0:
        return 0.0

    metadata = metadata or {}

    # PLACEHOLDER: Reglas simplificadas actuales
    # ============================================

    # Caso 1: Subvención directa (por defecto)
    if instrumento is None or instrumento == TipoInstrumento.SUBVENCION_DIRECTA:
        return importe_nominal

    # Caso 2: Préstamo con tipo de interés preferente
    elif instrumento == TipoInstrumento.PRESTAMO:
        return _calcular_equivalente_prestamo_placeholder(
            importe_nominal,
            fecha_concesion,
            metadata
        )

    # Caso 3: Garantía
    elif instrumento == TipoInstrumento.GARANTIA:
        return _calcular_equivalente_garantia_placeholder(
            importe_nominal,
            fecha_concesion,
            metadata
        )

    # Caso 4: Aportación de capital
    elif instrumento == TipoInstrumento.CAPITAL:
        # Placeholder: 100% del capital aportado
        # TODO: Aplicar "private investor test" según casos
        return importe_nominal

    # Caso 5: Ventaja fiscal
    elif instrumento == TipoInstrumento.VENTAJA_FISCAL:
        # Placeholder: 100% de la reducción fiscal
        return importe_nominal

    # Caso 6: Otros instrumentos
    else:
        logger.warning(
            f"Instrumento no reconocido '{instrumento}'. "
            f"Usando importe nominal como equivalente."
        )
        return importe_nominal


def _calcular_equivalente_prestamo_placeholder(
    importe_nominal: float,
    fecha_concesion: date,
    metadata: Dict[str, Any]
) -> float:
    """
    PLACEHOLDER: Cálculo simplificado de equivalente para préstamos.

    METODOLOGÍA CORRECTA (pendiente):
    =================================
    ESG = VAN(Intereses mercado) - VAN(Intereses aplicados)

    Donde:
    - Tipo de mercado = Tipo de referencia + Margen según rating
    - Tipo de referencia = Euribor/IRS según plazo
    - Margen = Según rating crediticio del beneficiario
    - Tasa de descuento = Tipo de referencia del momento

    REGLA PLACEHOLDER ACTUAL:
    =========================
    ESG ≈ 15% del principal para préstamos < 5 años
    ESG ≈ 25% del principal para préstamos >= 5 años

    Args:
        importe_nominal: Principal del préstamo
        fecha_concesion: Fecha de concesión
        metadata: plazo_meses, tipo_interes, etc.

    Returns:
        Equivalente aproximado
    """
    plazo_meses = metadata.get("plazo_meses", 60)

    if plazo_meses < 60:
        # < 5 años: ~15% del principal
        return importe_nominal * 0.15
    else:
        # >= 5 años: ~25% del principal
        return importe_nominal * 0.25


def _calcular_equivalente_garantia_placeholder(
    importe_nominal: float,
    fecha_concesion: date,
    metadata: Dict[str, Any]
) -> float:
    """
    PLACEHOLDER: Cálculo simplificado de equivalente para garantías.

    METODOLOGÍA CORRECTA (pendiente):
    =================================
    ESG = Prima de garantía según:
    - Importe garantizado
    - Duración de la garantía
    - Rating del beneficiario
    - Cobertura (% del riesgo cubierto)

    Tablas oficiales de primas según Comunicación CE sobre garantías.

    REGLA PLACEHOLDER ACTUAL:
    =========================
    ESG = 5% del importe garantizado (promedio simplificado)

    Args:
        importe_nominal: Importe garantizado
        fecha_concesion: Fecha de concesión
        metadata: porcentaje_garantia, rating, plazo_meses, etc.

    Returns:
        Equivalente aproximado
    """
    porcentaje_garantia = metadata.get("porcentaje_garantia", 80) / 100.0

    # Placeholder: 5% del importe garantizado
    return importe_nominal * porcentaje_garantia * 0.05


def validar_limite_de_minimis(
    beneficiario_id: str,
    importe_equivalente_nuevo: float,
    fecha_concesion: date,
    periodo_ventana_anos: int = 3
) -> Dict[str, Any]:
    """
    Valida que una nueva ayuda de minimis no supere los límites establecidos.

    LÍMITES DE MINIMIS (según Reglamento UE 2023/2831):
    ====================================================
    - General: 300.000 € en 3 ejercicios fiscales
    - Transporte por carretera: 100.000 € en 3 ejercicios
    - Sector agrícola: 20.000 € en 3 ejercicios
    - Sector pesquero: 30.000 € en 3 ejercicios

    TODO: Implementar consulta real a BD de concesiones del beneficiario

    Args:
        beneficiario_id: UUID del beneficiario
        importe_equivalente_nuevo: ESG de la nueva ayuda
        fecha_concesion: Fecha de concesión
        periodo_ventana_anos: Ventana temporal (por defecto 3 años)

    Returns:
        Dict con:
            - valido: bool
            - acumulado_previo: float (€)
            - acumulado_total: float (€)
            - limite_aplicable: float (€)
            - margen_restante: float (€)
    """
    # TODO: Implementar consulta real a BD
    # SELECT SUM(importe_equivalente)
    # FROM concesion
    # WHERE beneficiario_id = :id
    #   AND regimen_ayuda = 'de minimis'
    #   AND fecha_concesion >= :fecha_inicio_ventana

    # PLACEHOLDER: Asumir sin ayudas previas
    acumulado_previo = 0.0
    acumulado_total = acumulado_previo + importe_equivalente_nuevo

    # Límite general (puede variar según sector)
    limite_aplicable = 300_000.0

    return {
        "valido": acumulado_total <= limite_aplicable,
        "acumulado_previo": acumulado_previo,
        "acumulado_total": acumulado_total,
        "limite_aplicable": limite_aplicable,
        "margen_restante": max(0, limite_aplicable - acumulado_total)
    }
