"""
Pruebas del issue #28: abrir el chat con mi propia cuenta respondía error 500.
Ejecutar desde la raíz del proyecto: python -m unittest discover -s tests -v

Usan una base de datos temporal con el esquema real; no tocan agora.db.
"""

import os
import sqlite3
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from backend import aplicacion as agora  # noqa: E402
from backend.servicios import mensajes as servicio  # noqa: E402

ANA, BETO, CAMI = 1, 2, 3


class ChatPropioBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_original = agora.DB
        agora.DB = os.path.join(self.tmp.name, 'test.db')
        agora.app.config['TESTING'] = True

        conn = sqlite3.connect(agora.DB)
        with open(os.path.join(RAIZ, 'scripts', 'esquema.sql'), encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.executemany(
            "INSERT INTO usuarios (id, nombre, correo, password, carrera, universidad) "
            "VALUES (?, ?, ?, 'x', 'Sistemas', 'Univalle')",
            [(ANA, 'Ana', 'ana@test.edu'), (BETO, 'Beto', 'beto@test.edu'), (CAMI, 'Cami', 'cami@test.edu')],
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        agora.DB = self.db_original
        self.tmp.cleanup()

    def cliente(self, user_id):
        client = agora.app.test_client()
        with client.session_transaction() as s:
            s.update(user_id=user_id, nombre='N', carrera='Sistemas',
                     universidad='Univalle', rol='estudiante')
        return client

    def total_conversaciones(self):
        conn = agora.get_db()
        try:
            return conn.execute("SELECT COUNT(*) AS total FROM conversaciones").fetchone()['total']
        finally:
            conn.close()


class AbrirChatConmigoMismo(ChatPropioBase):
    def test_sin_conversaciones_no_da_error_500(self):
        respuesta = self.cliente(ANA).get(f'/mensajes/{ANA}')
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.headers['Location'].endswith('/mensajes'))
        self.assertEqual(self.total_conversaciones(), 0)

    def test_muestra_el_aviso_en_la_lista_de_mensajes(self):
        respuesta = self.cliente(ANA).get(f'/mensajes/{ANA}', follow_redirects=True)
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('No puedes abrir un chat contigo mismo.', respuesta.get_data(as_text=True))

    def test_con_otras_conversaciones_no_abre_la_de_otra_persona(self):
        # Antes, si Ana ya tenía un chat con Beto, /mensajes/<Ana> le abría ese chat.
        cliente = self.cliente(ANA)
        cliente.get(f'/mensajes/{BETO}')
        antes = self.total_conversaciones()
        respuesta = cliente.get(f'/mensajes/{ANA}')
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(self.total_conversaciones(), antes)

    def test_el_servicio_no_crea_una_conversacion_con_uno_mismo(self):
        conn = agora.get_db()
        try:
            with self.assertRaises(ValueError):
                servicio.obtener_o_crear_conversacion(conn, ANA, ANA)
        finally:
            conn.close()


class ChatConOtraPersona(ChatPropioBase):
    def test_abrir_chat_con_otra_persona_sigue_funcionando(self):
        respuesta = self.cliente(ANA).get(f'/mensajes/{CAMI}')
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(self.total_conversaciones(), 1)


if __name__ == '__main__':
    unittest.main()
