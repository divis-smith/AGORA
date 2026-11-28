"""
Pruebas del issue #29: los datos de demostración tienen fechas relativas a hoy (RNF-07, RF-26).
Ejecutar desde la raíz del proyecto: python -m unittest discover -s tests -v

Crean la base de demostración completa en una carpeta temporal; no tocan agora.db.
"""

import contextlib
import io
import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import date
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.servicios import eventos, moderacion  # noqa: E402
from scripts import crear_db  # noqa: E402
from scripts.datos_demo import DIAS_HASTA_EVENTOS, fechas_eventos_demo  # noqa: E402


class FechasEventosDemoTest(unittest.TestCase):
    """La función que calcula las fechas, sin base de datos."""

    def test_cuenta_los_dias_desde_la_fecha_dada(self):
        fechas = fechas_eventos_demo(date(2026, 12, 30))
        self.assertEqual(fechas, ['2027-01-06', '2027-01-11', '2027-01-16', '2027-01-19'])

    def test_todas_las_fechas_son_futuras(self):
        hoy = date(2030, 2, 25)
        for fecha in fechas_eventos_demo(hoy):
            self.assertGreater(fecha, hoy.isoformat())

    def test_hay_una_fecha_por_evento(self):
        self.assertEqual(len(fechas_eventos_demo()), len(DIAS_HASTA_EVENTOS))


class BaseDemoTest(unittest.TestCase):
    """La base creada con scripts/crear_db.py, como en el README."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        ruta = os.path.join(self.tmp.name, 'demo.db')
        with mock.patch.dict(os.environ, {'DATABASE_PATH': ruta}), \
                contextlib.redirect_stdout(io.StringIO()):
            crear_db.crear_base_datos()
        self.conn = sqlite3.connect(ruta)
        self.conn.row_factory = sqlite3.Row

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_ningun_evento_demo_quedo_en_el_pasado(self):
        pasados = self.conn.execute(
            "SELECT COUNT(*) AS n FROM eventos WHERE fecha < date('now')"
        ).fetchone()['n']
        self.assertEqual(pasados, 0)

    def test_la_lista_de_eventos_muestra_todos_los_de_demo(self):
        total = self.conn.execute("SELECT COUNT(*) AS n FROM eventos").fetchone()['n']
        estudiante = self.conn.execute(
            "SELECT id FROM usuarios WHERE correo = 'vale@correounivalle.edu'"
        ).fetchone()['id']

        proximos = eventos.listar_proximos(self.conn, estudiante, None)

        self.assertEqual(len(proximos), total)
        self.assertIn('Hackathon Univalle 2026 — retos de IA', [e['titulo'] for e in proximos])

    def test_el_panel_cuenta_los_eventos_de_demo(self):
        totales = moderacion.totales_panel(self.conn)
        self.assertGreater(totales['total_eventos'], 0)


if __name__ == '__main__':
    unittest.main()
