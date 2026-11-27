"""
Pruebas de los comentarios en proyectos del portafolio (Issue #35).
Ejecutar desde la raíz del proyecto: python -m unittest discover -s tests -v

Usan una base de datos temporal; no tocan data/.
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
from backend.servicios import portafolio as servicio  # noqa: E402

CORREO = 'ana@test.edu'
PASSWORD = 'clave-de-prueba'


class ComentarProyectoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_original = agora.DB
        agora.DB = os.path.join(self.tmp.name, 'test.db')
        agora.app.config['TESTING'] = True

        conn = sqlite3.connect(agora.DB)
        conn.executescript((RAIZ / 'scripts' / 'esquema.sql').read_text(encoding='utf-8'))
        clave = generate_password_hash(PASSWORD)
        conn.execute("INSERT INTO usuarios (nombre, correo, password) VALUES (?,?,?)",
                     ('Ana', CORREO, clave))
        conn.execute("INSERT INTO usuarios (nombre, correo, password) VALUES (?,?,?)",
                     ('Luis', 'luis@test.edu', clave))
        conn.execute("INSERT INTO proyectos (autor_id, titulo, descripcion) VALUES (2, 'Mi app', 'Una app')")
        conn.commit()
        conn.close()

        self.client = agora.app.test_client()
        self.client.post('/login', data={'correo': CORREO, 'password': PASSWORD})

    def tearDown(self):
        agora.DB = self.db_original
        self.tmp.cleanup()

    def _comentarios(self):
        conn = agora.get_db()
        filas = conn.execute(
            "SELECT proyecto_id, autor_id, contenido FROM comentarios_proyecto ORDER BY id").fetchall()
        conn.close()
        return [dict(fila) for fila in filas]

    def _comentar(self, contenido, proyecto_id=1, seguir=True):
        return self.client.post(f'/portafolio/{proyecto_id}/comentar', data={'contenido': contenido},
                                follow_redirects=seguir)

    def test_comentar_guarda_el_comentario_y_lo_muestra_con_mi_nombre(self):
        respuesta = self._comentar('Muy buen trabajo')
        html = respuesta.get_data(as_text=True)
        self.assertIn('Comentario publicado.', html)
        self.assertIn('Muy buen trabajo', html)
        self.assertIn('Ana', html)
        self.assertEqual(self._comentarios(),
                         [{'proyecto_id': 1, 'autor_id': 1, 'contenido': 'Muy buen trabajo'}])

    def test_comentar_vuelve_al_detalle_en_la_seccion_de_comentarios(self):
        respuesta = self._comentar('Hola', seguir=False)
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.headers['Location'].endswith('/portafolio/1#comentarios'))

    def test_el_comentario_se_guarda_sin_espacios_sobrantes(self):
        self._comentar('   con espacios   ')
        self.assertEqual(self._comentarios()[0]['contenido'], 'con espacios')

    def test_un_comentario_vacio_no_se_guarda(self):
        html = self._comentar('').get_data(as_text=True)
        self.assertIn('El comentario no puede estar vacío.', html)
        self.assertEqual(self._comentarios(), [])

    def test_un_comentario_de_solo_espacios_cuenta_como_vacio(self):
        html = self._comentar('    \n  ').get_data(as_text=True)
        self.assertIn('El comentario no puede estar vacío.', html)
        self.assertEqual(self._comentarios(), [])

    def test_un_comentario_de_mas_de_1000_caracteres_no_se_guarda(self):
        html = self._comentar('a' * 1001).get_data(as_text=True)
        self.assertIn('El comentario no puede superar 1000 caracteres.', html)
        self.assertEqual(self._comentarios(), [])

    def test_un_comentario_de_exactamente_1000_caracteres_si_se_guarda(self):
        self._comentar('a' * 1000)
        self.assertEqual(len(self._comentarios()), 1)

    def test_comentar_un_proyecto_que_no_existe_lleva_al_portafolio_con_mensaje(self):
        respuesta = self._comentar('Hola', proyecto_id=999, seguir=False)
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.headers['Location'].endswith('/portafolio'))
        seguida = self.client.get('/portafolio')
        self.assertIn('Proyecto no encontrado.', seguida.get_data(as_text=True))
        self.assertEqual(self._comentarios(), [])

    def test_comentar_exige_iniciar_sesion(self):
        anonimo = agora.app.test_client()
        respuesta = anonimo.post('/portafolio/1/comentar', data={'contenido': 'Hola'})
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login', respuesta.headers['Location'])
        self.assertEqual(self._comentarios(), [])

    def test_el_servicio_rechaza_proyectos_inexistentes(self):
        conn = agora.get_db()
        with self.assertRaises(ValueError):
            servicio.comentar(conn, 999, 1, 'Hola')
        conn.close()

    def test_el_detalle_ofrece_el_formulario_para_comentar(self):
        html = self.client.get('/portafolio/1').get_data(as_text=True)
        self.assertIn('action="/portafolio/1/comentar"', html)
        self.assertIn('name="contenido"', html)
        self.assertIn('maxlength="1000"', html)
        self.assertIn('id="comentarios"', html)

    def test_el_comentario_publicado_se_ve_en_el_detalle_y_cuenta_en_el_titulo(self):
        self._comentar('Primer comentario')
        self._comentar('Segundo comentario')
        html = self.client.get('/portafolio/1').get_data(as_text=True)
        self.assertIn('Comentarios (2)', html)
        self.assertLess(html.index('Primer comentario'), html.index('Segundo comentario'))


if __name__ == '__main__':
    unittest.main()
