"""
Pruebas de la agenda de los eventos (Issue #40).
Ejecutar desde la raíz del proyecto: python -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from backend.nucleo.utilidades import parsear_agenda, procesar_evento  # noqa: E402

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


if __name__ == '__main__':
    unittest.main()
