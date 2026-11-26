"""
Pruebas del issue #24: el perfil público no debe mostrar publicaciones anónimas.
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

AUTORA, VISITANTE = 1, 2


class PerfilSinAnonimasBase(unittest.TestCase):
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
            [(AUTORA, 'Autora', 'autora@test.edu'), (VISITANTE, 'Visitante', 'visitante@test.edu')],
        )
        conn.executemany(
            "INSERT INTO publicaciones (autor_id, titulo, contenido, es_anonimo) VALUES (?, ?, 'c', ?)",
            [(AUTORA, 'Post con mi nombre', 0), (AUTORA, 'Post anonimo secreto', 1)],
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

    def html(self, user_id, ruta):
        respuesta = self.cliente(user_id).get(ruta)
        self.assertEqual(respuesta.status_code, 200)
        return respuesta.get_data(as_text=True)


class PerfilPublico(PerfilSinAnonimasBase):
    def test_otro_usuario_no_ve_la_anonima(self):
        html = self.html(VISITANTE, f'/perfil/{AUTORA}')
        self.assertIn('Post con mi nombre', html)
        self.assertNotIn('Post anonimo secreto', html)

    def test_el_contador_no_cuenta_la_anonima(self):
        from backend.servicios import social
        conn = agora.get_db()
        try:
            self.assertEqual(social.contar_publicaciones(conn, AUTORA, incluir_anonimas=False), 1)
            self.assertEqual(social.contar_publicaciones(conn, AUTORA), 2)
        finally:
            conn.close()

    def test_la_autora_si_ve_su_anonima_en_su_perfil_publico(self):
        html = self.html(AUTORA, f'/perfil/{AUTORA}')
        self.assertIn('Post con mi nombre', html)
        self.assertIn('Post anonimo secreto', html)

    def test_la_autora_ve_su_anonima_en_su_perfil_propio(self):
        html = self.html(AUTORA, '/perfil')
        self.assertIn('Post anonimo secreto', html)


if __name__ == '__main__':
    unittest.main()
