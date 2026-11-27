"""Configuración de la aplicación a partir de variables de entorno."""

import os
from pathlib import Path


RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_BASE_DATOS = RAIZ_PROYECTO / 'data' / 'agora.db'

ENTORNOS = {'desarrollo', 'produccion'}
CLAVE_DESARROLLO = 'dev-only-change-me'
# Valores que nunca sirven fuera de desarrollo: el de por defecto y el de .env.example.
CLAVES_INSEGURAS = {CLAVE_DESARROLLO, 'replace-with-a-random-value'}
LARGO_MINIMO_CLAVE = 32


class ConfiguracionInvalida(RuntimeError):
    """La configuración no permite arrancar la aplicación de forma segura."""


def _validar_clave_produccion(clave):
    if not clave:
        raise ConfiguracionInvalida(
            'AGORA_ENTORNO=produccion exige definir SECRET_KEY. '
            'Genera una con: python -c "import secrets; print(secrets.token_hex(32))"'
        )
    if clave in CLAVES_INSEGURAS:
        raise ConfiguracionInvalida(
            'SECRET_KEY tiene un valor de ejemplo o de desarrollo; '
            'en producción usa una clave aleatoria propia.'
        )
    if len(clave) < LARGO_MINIMO_CLAVE:
        raise ConfiguracionInvalida(
            f'SECRET_KEY es muy corta: en producción debe tener al menos {LARGO_MINIMO_CLAVE} caracteres.'
        )


def obtener_configuracion(entorno=None) -> dict[str, object]:
    """Devuelve la configuración de ejecución de ÁGORA.

    Fuera del modo desarrollo, SECRET_KEY es obligatoria y no puede ser
    un valor de ejemplo (Issue #39). En desarrollo se mantiene la clave
    por defecto para que el proyecto arranque sin configurar nada.
    """
    variables = os.environ if entorno is None else entorno

    modo = variables.get('AGORA_ENTORNO', 'desarrollo').strip().lower()
    if modo not in ENTORNOS:
        raise ConfiguracionInvalida(
            f'AGORA_ENTORNO debe ser "desarrollo" o "produccion", no "{modo}".'
        )

    clave = variables.get('SECRET_KEY', '').strip()
    if modo == 'produccion':
        _validar_clave_produccion(clave)
    else:
        clave = clave or CLAVE_DESARROLLO

    return {
        'ENTORNO': modo,
        'SECRET_KEY': clave,
        'DATABASE_PATH': variables.get('DATABASE_PATH', str(RUTA_BASE_DATOS)),
        'FLASK_DEBUG': variables.get('FLASK_DEBUG', '').lower()
        in {'1', 'true', 'yes'},
    }
