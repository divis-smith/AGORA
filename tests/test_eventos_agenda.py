"""
Pruebas de la agenda de los eventos (Issue #40).
Ejecutar desde la raíz del proyecto: python -m unittest discover -s tests -v
"""

import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

from werkzeug.security import generate_password_hash

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from backend import aplicacion as agora  # noqa: E402
from backend.nucleo.utilidades import parsear_agenda, procesar_evento  # noqa: E402

CORREO = 'ana@test.edu'
PASSWORD = 'clave-de-prueba'

AGENDA = ('[{"hora":"09:00","item":"Apertura y registro"},'
          '{"hora":"10:00","item":"Inicio del hackathon"}]')


class ParsearAgendaTest(unittest.TestCase):
    def test_una_lista_json_se_convierte_en_filas_de_hora_y_actividad(self):
        actividades, texto = parsear_agenda(AGENDA)
        self.assertEqual(actividades, [
            {'hora': '09:00', 'item': 'Apertura y registro'},
            {'hora': '10:00', 'item': 'Inicio del hackathon'},
        ])
        self.assertEqual(texto, '')

    def test_sin_agenda_no_hay_actividades_ni_texto(self):
        for vacia in (None, '', '   ', '[]'):
            with self.subTest(agenda=vacia):
                self.assertEqual(parsear_agenda(vacia), ([], ''))

    def test_un_texto_que_no_es_json_se_devuelve_tal_cual(self):
        actividades, texto = parsear_agenda('  9:00 Apertura, 10:00 Charla  ')
        self.assertEqual(actividades, [])
        self.assertEqual(texto, '9:00 Apertura, 10:00 Charla')

    def test_un_json_que_no_es_una_lista_se_trata_como_texto(self):
        for texto_json in ('{"hora":"09:00"}', '"solo texto"', '42'):
            with self.subTest(agenda=texto_json):
                actividades, texto = parsear_agenda(texto_json)
                self.assertEqual(actividades, [])
                self.assertEqual(texto, texto_json)

    def test_una_actividad_sin_hora_se_muestra_solo_con_su_texto(self):
        actividades, _ = parsear_agenda('[{"item":"Cierre"}]')
        self.assertEqual(actividades, [{'hora': '', 'item': 'Cierre'}])

    def test_se_ignoran_los_elementos_sin_actividad(self):
        actividades, texto = parsear_agenda('[{"hora":"09:00"}, null, {"hora":"10:00","item":"Charla"}]')
        self.assertEqual(actividades, [{'hora': '10:00', 'item': 'Charla'}])
        self.assertEqual(texto, '')

    def test_un_elemento_que_es_texto_se_toma_como_actividad(self):
        actividades, _ = parsear_agenda('["Apertura", "Cierre"]')
        self.assertEqual([a['item'] for a in actividades], ['Apertura', 'Cierre'])


class ProcesarEventoAgendaTest(unittest.TestCase):
    def test_procesar_evento_agrega_la_agenda_ya_convertida(self):
        evento = procesar_evento({'fecha': '2026-06-15', 'agenda': AGENDA})
        self.assertEqual(len(evento['agenda_items']), 2)
        self.assertEqual(evento['agenda_items'][0]['hora'], '09:00')
        self.assertEqual(evento['agenda_texto'], '')

    def test_procesar_evento_sin_columna_de_agenda_no_falla(self):
        evento = procesar_evento({'fecha': '2026-06-15'})
        self.assertEqual(evento['agenda_items'], [])
        self.assertEqual(evento['agenda_texto'], '')


class AgendaEnElDetalleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_original = agora.DB
        agora.DB = os.path.join(self.tmp.name, 'test.db')
        agora.app.config['TESTING'] = True

        conn = sqlite3.connect(agora.DB)
        conn.executescript((RAIZ / 'scripts' / 'esquema.sql').read_text(encoding='utf-8'))
        conn.execute("INSERT INTO usuarios (nombre, correo, password) VALUES (?,?,?)",
                     ('Ana', CORREO, generate_password_hash(PASSWORD)))
        agendas = [
            ('Hackathon Univalle 2026 — retos de IA', AGENDA),
            ('Evento sin agenda', None),
            ('Evento con agenda vacía', '[]'),
            ('Evento con texto plano', '9:00 Apertura y 10:00 Charla'),
            ('Evento con JSON roto', '[{"hora": "09:00", "item": "Apertura"'),
            ('Evento con HTML', '[{"hora":"09:00","item":"<b>Negrita</b>"}]'),
        ]
        for titulo, agenda in agendas:
            conn.execute("INSERT INTO eventos (creador_id, titulo, fecha, agenda) VALUES (1, ?, '2026-06-15', ?)",
                         (titulo, agenda))
        conn.commit()
        conn.close()

        self.client = agora.app.test_client()
        self.client.post('/login', data={'correo': CORREO, 'password': PASSWORD})

    def tearDown(self):
        agora.DB = self.db_original
        self.tmp.cleanup()

    def _detalle(self, evento_id):
        respuesta = self.client.get(f'/eventos/{evento_id}')
        self.assertEqual(respuesta.status_code, 200)
        return respuesta.get_data(as_text=True)

    def test_el_hackathon_muestra_cada_actividad_en_su_fila_con_su_hora(self):
        html = self._detalle(1)
        self.assertIn('>Agenda</div>', html)
        self.assertIn('<span class="agenda-hora">09:00</span>', html)
        self.assertIn('<span class="agenda-texto">Apertura y registro</span>', html)
        self.assertIn('<span class="agenda-hora">10:00</span>', html)
        self.assertIn('<span class="agenda-texto">Inicio del hackathon</span>', html)
        self.assertEqual(html.count('class="agenda-item"'), 2)

    def test_el_hackathon_no_muestra_llaves_ni_comillas_del_formato_json(self):
        html = self._detalle(1)
        self.assertNotIn('"hora"', html)
        self.assertNotIn('&#34;hora&#34;', html)
        self.assertNotIn('[{', html)

    def test_un_evento_sin_agenda_no_muestra_la_seccion(self):
        self.assertNotIn('>Agenda</div>', self._detalle(2))

    def test_una_agenda_vacia_tampoco_muestra_la_seccion(self):
        self.assertNotIn('>Agenda</div>', self._detalle(3))

    def test_una_agenda_en_texto_plano_se_muestra_sin_romper_la_pagina(self):
        html = self._detalle(4)
        self.assertIn('>Agenda</div>', html)
        self.assertIn('9:00 Apertura y 10:00 Charla', html)
        self.assertNotIn('agenda-item', html)

    def test_un_json_roto_se_muestra_como_texto_sin_romper_la_pagina(self):
        html = self._detalle(5)
        self.assertIn('>Agenda</div>', html)
        self.assertNotIn('agenda-item', html)

    def test_el_texto_de_la_agenda_se_escapa(self):
        html = self._detalle(6)
        self.assertIn('&lt;b&gt;Negrita&lt;/b&gt;', html)
        self.assertNotIn('<b>Negrita</b>', html)


if __name__ == '__main__':
    unittest.main()
