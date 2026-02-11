"""
Utilidades para interpretar NIFs y determinar formas jurídicas.

Basado en la Orden EHA/451/2008 (en vigor desde 1 de julio de 2008).
"""

# Mapeo de letras iniciales de NIF a formas jurídicas
FORMAS_JURIDICAS_NIF = {
    'A': 'Sociedad Anónima (SA)',
    'B': 'Sociedad de Responsabilidad Limitada (SL)',
    'C': 'Sociedad Colectiva',
    'D': 'Sociedad Comanditaria',
    'E': 'Comunidades de Bienes',
    'F': 'Sociedad Cooperativa',
    'G': 'Asociaciones',
    'H': 'Comunidades de Propietarios en régimen de propiedad horizontal',
    'J': 'Sociedades Civiles (con o sin personalidad jurídica)',
    'N': 'Entidades no residentes en España',
    'P': 'Corporaciones Locales',
    'Q': 'Organismos Públicos',
    'R': 'Congregaciones e instituciones religiosas',
    'S': 'Órganos de la Administración del Estado y Comunidades Autónomas',
    'U': 'Uniones Temporales de Empresas (UTE)',
    'V': 'Otros tipos no definidos',
    'W': 'Establecimientos permanentes de entidades no residentes en España',
}


def interpretar_forma_juridica_desde_nif(nif: str) -> str:
    """
    Interpreta la forma jurídica a partir del NIF según las reglas de la Orden EHA/451/2008.

    Reglas:
    1. Si el NIF contiene asteriscos (*) → "Persona física" (anonimizado por RGPD)
    2. Si el NIF comienza con una letra de persona jurídica → Interpretar según tabla oficial
    3. Si el NIF comienza con dígito → "Persona física" (DNI/NIE)
    4. Otros casos → "Desconocido"

    Args:
        nif: NIF o CIF del beneficiario (puede estar anonimizado)

    Returns:
        str: Forma jurídica interpretada

    Examples:
        >>> interpretar_forma_juridica_desde_nif("A12345678")
        'Sociedad Anónima (SA)'

        >>> interpretar_forma_juridica_desde_nif("B87654321")
        'Sociedad de Responsabilidad Limitada (SL)'

        >>> interpretar_forma_juridica_desde_nif("****5678A")
        'Persona física'

        >>> interpretar_forma_juridica_desde_nif("12345678Z")
        'Persona física'

        >>> interpretar_forma_juridica_desde_nif(None)
        'Desconocido'
    """
    if not nif:
        return "Desconocido"

    nif_clean = nif.strip().upper()

    # Caso 1: NIF anonimizado (contiene asteriscos)
    if '*' in nif_clean:
        return "Persona física"

    # Caso 2: NIF vacío o demasiado corto
    if len(nif_clean) < 1:
        return "Desconocido"

    # Obtener primer caracter
    primer_char = nif_clean[0]

    # Caso 3: NIF de persona jurídica (comienza con letra conocida)
    if primer_char in FORMAS_JURIDICAS_NIF:
        return FORMAS_JURIDICAS_NIF[primer_char]

    # Caso 4: NIF de persona física (comienza con dígito)
    if primer_char.isdigit():
        return "Persona física"

    # Caso 5: NIE (Número de Identificación de Extranjero) - comienza con X, Y o Z
    if primer_char in ('X', 'Y', 'Z'):
        return "Persona física"

    # Caso 6: Letra no reconocida
    return "Desconocido"


def es_persona_fisica(nif: str) -> bool:
    """
    Determina si un NIF corresponde a una persona física.

    Args:
        nif: NIF o CIF del beneficiario

    Returns:
        bool: True si es persona física, False en caso contrario
    """
    forma_juridica = interpretar_forma_juridica_desde_nif(nif)
    return forma_juridica == "Persona física"


def es_persona_juridica(nif: str) -> bool:
    """
    Determina si un NIF corresponde a una persona jurídica.

    Args:
        nif: NIF o CIF del beneficiario

    Returns:
        bool: True si es persona jurídica, False en caso contrario
    """
    forma_juridica = interpretar_forma_juridica_desde_nif(nif)
    return forma_juridica not in ("Persona física", "Desconocido")


def obtener_tipo_entidad_desde_nif(nif: str) -> str:
    """
    Obtiene el tipo de entidad (pública/privada) a partir del NIF.

    Args:
        nif: NIF o CIF del beneficiario

    Returns:
        str: "Pública", "Privada" o "Desconocido"
    """
    if not nif:
        return "Desconocido"

    nif_clean = nif.strip().upper()
    if len(nif_clean) < 1 or '*' in nif_clean:
        return "Desconocido"

    primer_char = nif_clean[0]

    # Entidades públicas
    entidades_publicas = {'P', 'Q', 'S'}
    if primer_char in entidades_publicas:
        return "Pública"

    # Entidades privadas (resto de letras de personas jurídicas)
    if primer_char in FORMAS_JURIDICAS_NIF:
        return "Privada"

    # Personas físicas
    if primer_char.isdigit() or primer_char in ('X', 'Y', 'Z'):
        return "Privada"

    return "Desconocido"


def obtener_codigo_natural_desde_nif(nif: str) -> str:
    """
    Obtiene el código natural (prefijo del NIF) para indexar en el catálogo de formas jurídicas.

    Args:
        nif: NIF o CIF del beneficiario

    Returns:
        str: Código natural (*, A-W, o ?)

    Examples:
        >>> obtener_codigo_natural_desde_nif("A12345678")
        'A'

        >>> obtener_codigo_natural_desde_nif("****5678A")
        '*'

        >>> obtener_codigo_natural_desde_nif("12345678Z")
        '*'

        >>> obtener_codigo_natural_desde_nif("X1234567L")
        '*'
    """
    if not nif:
        return "?"

    nif_clean = nif.strip().upper()

    # Caso 1: NIF anonimizado (contiene asteriscos) → Persona física
    if '*' in nif_clean:
        return "*"

    # Caso 2: NIF vacío o demasiado corto
    if len(nif_clean) < 1:
        return "?"

    primer_char = nif_clean[0]

    # Caso 3: NIF de persona jurídica (comienza con letra conocida)
    if primer_char in FORMAS_JURIDICAS_NIF:
        return primer_char

    # Caso 4: NIF de persona física (comienza con dígito)
    if primer_char.isdigit():
        return "*"

    # Caso 5: NIE (Número de Identificación de Extranjero) → Persona física
    if primer_char in ('X', 'Y', 'Z'):
        return "*"

    # Caso 6: Letra no reconocida
    return "?"
