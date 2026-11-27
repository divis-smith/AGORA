"""
Pruebas del issue #39: SECRET_KEY obligatoria fuera del modo desarrollo.
Ejecutar desde la raíz del proyecto: python -m unittest discover -s tests -v

No arrancan la aplicación: prueban la función que lee la configuración
con variables de entorno de mentira.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.nucleo.configuracion import (  # noqa: E402
    CLAVE_DESARROLLO,
    ConfiguracionInvalida,
    obtener_configuracion,
)

CLAVE_BUENA = 'a' * 64


class ModoDesarrollo(unittest.TestCase):
    def test_sin_variables_arranca_en_desarrollo_con_la_clave_por_defecto(self):
        config = obtener_configuracion({})
        self.assertEqual(config['ENTORNO'], 'desarrollo')
        self.assertEqual(config['SECRET_KEY'], CLAVE_DESARROLLO)

    def test_en_desarrollo_respeta_la_clave_si_la_definen(self):
        config = obtener_configuracion({'SECRET_KEY': CLAVE_BUENA})
        self.assertEqual(config['SECRET_KEY'], CLAVE_BUENA)


class ModoProduccion(unittest.TestCase):
    def test_sin_secret_key_no_arranca(self):
        with self.assertRaises(ConfiguracionInvalida):
            obtener_configuracion({'AGORA_ENTORNO': 'produccion'})

    def test_con_la_clave_de_desarrollo_no_arranca(self):
        with self.assertRaises(ConfiguracionInvalida):
            obtener_configuracion({'AGORA_ENTORNO': 'produccion', 'SECRET_KEY': CLAVE_DESARROLLO})

    def test_con_la_clave_de_ejemplo_del_env_example_no_arranca(self):
        with self.assertRaises(ConfiguracionInvalida):
            obtener_configuracion({'AGORA_ENTORNO': 'produccion',
                                   'SECRET_KEY': 'replace-with-a-random-value'})

    def test_con_una_clave_corta_no_arranca(self):
        with self.assertRaises(ConfiguracionInvalida):
            obtener_configuracion({'AGORA_ENTORNO': 'produccion', 'SECRET_KEY': 'corta123'})

    def test_con_una_clave_aleatoria_arranca(self):
        config = obtener_configuracion({'AGORA_ENTORNO': 'produccion', 'SECRET_KEY': CLAVE_BUENA})
        self.assertEqual(config['ENTORNO'], 'produccion')
        self.assertEqual(config['SECRET_KEY'], CLAVE_BUENA)

    def test_acepta_mayusculas_y_espacios_en_el_entorno(self):
        config = obtener_configuracion({'AGORA_ENTORNO': ' Produccion ', 'SECRET_KEY': CLAVE_BUENA})
        self.assertEqual(config['ENTORNO'], 'produccion')


class EntornoDesconocido(unittest.TestCase):
    def test_un_valor_raro_no_arranca(self):
        with self.assertRaises(ConfiguracionInvalida):
            obtener_configuracion({'AGORA_ENTORNO': 'prod'})


if __name__ == '__main__':
    unittest.main()
