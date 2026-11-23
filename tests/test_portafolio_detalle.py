"""
Pruebas del detalle de un proyecto del portafolio (Issue #34).
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


class DetalleProyectoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_original = agora.DB
        agora.DB = os.path.join(self.tmp.name, 'test.db')
        agora.app.config['TESTING'] = True

        conn = sqlite3.connect(agora.DB)
        conn.executescript((RAIZ / 'scripts' / 'esquema.sql').read_text(encoding='utf-8'))
        clave = generate_password_hash(PASSWORD)
        conn.execute("INSERT INTO usuarios (nombre, correo, password, carrera) VALUES (?,?,?,?)",
                     ('Ana', CORREO, clave, 'Sistemas'))
        conn.execute("INSERT INTO usuarios (nombre, correo, password) VALUES (?,?,?)",
                     ('Luis', 'luis@test.edu', clave))
        conn.execute(
            "INSERT INTO proyectos (autor_id, titulo, descripcion, tecnologias, estado, repo_url, demo_url) "
            "VALUES (2, 'Mi app', 'Una app', '[\"Flask\",\"SQLite\"]', 'completado', "
            "'https://github.com/luis/app', 'https://app.test')")
        conn.execute("INSERT INTO comentarios_proyecto (proyecto_id, autor_id, contenido) "
                     "VALUES (1, 1, 'Muy buen trabajo')")
        conn.commit()
        conn.close()

        self.client = agora.app.test_client()
        self.client.post('/login', data={'correo': CORREO, 'password': PASSWORD})

    def tearDown(self):
        agora.DB = self.db_original
        self.tmp.cleanup()

    def test_obtener_detalle_incluye_autor_aplausos_y_tecnologias(self):
        conn = agora.get_db()
        proyecto = servicio.obtener_detalle(conn, 1, 1)
        conn.close()
        self.assertEqual(proyecto['nombre_autor'], 'Luis')
        self.assertEqual(proyecto['total_aplausos'], 0)
        self.assertFalse(proyecto['ya_aplaudi'])
        self.assertEqual(proyecto['tecnologias_lista'], ['Flask', 'SQLite'])
        self.assertEqual(proyecto['repo_url'], 'https://github.com/luis/app')

    def test_obtener_detalle_marca_si_el_usuario_ya_aplaudio(self):
        conn = agora.get_db()
        servicio.alternar_aplauso(conn, 1, 1)
        proyecto = servicio.obtener_detalle(conn, 1, 1)
        otro = servicio.obtener_detalle(conn, 1, 2)
        conn.close()
        self.assertEqual(proyecto['total_aplausos'], 1)
        self.assertTrue(proyecto['ya_aplaudi'])
        self.assertFalse(otro['ya_aplaudi'])

    def test_obtener_detalle_de_proyecto_inexistente_devuelve_none(self):
        conn = agora.get_db()
        self.assertIsNone(servicio.obtener_detalle(conn, 999, 1))
        conn.close()

    def test_listar_comentarios_trae_el_nombre_del_autor(self):
        conn = agora.get_db()
        comentarios = servicio.listar_comentarios(conn, 1)
        conn.close()
        self.assertEqual(len(comentarios), 1)
        self.assertEqual(comentarios[0]['nombre_autor'], 'Ana')
        self.assertEqual(comentarios[0]['contenido'], 'Muy buen trabajo')

    def test_proyecto_que_no_existe_lleva_al_portafolio_con_mensaje(self):
        respuesta = self.client.get('/portafolio/999')
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.headers['Location'].endswith('/portafolio'))
        seguida = self.client.get('/portafolio')
        self.assertIn('Proyecto no encontrado.', seguida.get_data(as_text=True))

    def test_el_detalle_exige_iniciar_sesion(self):
        anonimo = agora.app.test_client()
        respuesta = anonimo.get('/portafolio/1')
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login', respuesta.headers['Location'])


if __name__ == '__main__':
    unittest.main()
