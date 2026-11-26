"""
Pruebas del issue #32: el administrador crea y elimina foros desde el panel (RF-39).
Ejecutar desde la raíz del proyecto: python -m unittest discover -s tests -v

Usan una base temporal creada con scripts/esquema.sql (el esquema real), para
comprobar que al eliminar un foro no quedan preguntas, respuestas ni votos huérfanos.
"""

import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from backend import aplicacion as agora  # noqa: E402
from backend.servicios import foros  # noqa: E402

ADMIN, MODERADOR, ESTUDIANTE = 1, 2, 3
FORO_CALCULO, FORO_OTRO = 1, 2


class ForosBase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.addCleanup(setattr, agora, 'DB', agora.DB)
        agora.DB = os.path.join(tmp.name, 'test.db')
        agora.app.config['TESTING'] = True

        conn = sqlite3.connect(agora.DB)
        conn.executescript((RAIZ / 'scripts' / 'esquema.sql').read_text(encoding='utf-8'))
        conn.executemany(
            "INSERT INTO usuarios (id, nombre, correo, password, rol) VALUES (?, ?, ?, 'x', ?)",
            [(ADMIN, 'Admin', 'admin@test.edu', 'admin'),
             (MODERADOR, 'Mod', 'mod@test.edu', 'moderador'),
             (ESTUDIANTE, 'Vale', 'vale@test.edu', 'estudiante')])
        conn.executemany(
            "INSERT INTO foros (id, nombre, categoria) VALUES (?, ?, ?)",
            [(FORO_CALCULO, 'Cálculo III', 'matematicas'), (FORO_OTRO, 'Vida Universitaria', 'campus')])
        # Cálculo III: una pregunta con una respuesta votada. El otro foro también
        # tiene contenido, que no debe tocarse al eliminar Cálculo III.
        for foro_id in (FORO_CALCULO, FORO_OTRO):
            pregunta = conn.execute(
                "INSERT INTO preguntas_foro (foro_id, autor_id, titulo) VALUES (?, ?, 'Duda')",
                (foro_id, ESTUDIANTE)).lastrowid
            respuesta = conn.execute(
                "INSERT INTO respuestas_foro (pregunta_id, autor_id, contenido) VALUES (?, ?, 'Así')",
                (pregunta, ADMIN)).lastrowid
            conn.execute("INSERT INTO votos_respuesta (usuario_id, respuesta_id) VALUES (?, ?)",
                         (ESTUDIANTE, respuesta))
        conn.commit()
        conn.close()

    def cliente(self, user_id=None):
        client = agora.app.test_client()
        if user_id is not None:
            conn = agora.get_db()
            u = conn.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
            conn.close()
            with client.session_transaction() as s:
                s.update(user_id=u['id'], nombre=u['nombre'], carrera=u['carrera'],
                         universidad=u['universidad'], rol=u['rol'])
        return client

    def conexion(self):
        conn = agora.get_db()
        self.addCleanup(conn.close)
        return conn

    def contar(self, sql, *params):
        conn = agora.get_db()
        n = conn.execute(sql, params).fetchone()[0]
        conn.close()
        return n

    def mensajes_flash(self, client):
        with client.session_transaction() as s:
            return [mensaje for _, mensaje in s.get('_flashes', [])]

    def crear(self, client, nombre, categoria='academico', descripcion=''):
        return client.post('/admin/foros', data={'accion': 'crear', 'nombre': nombre,
                                                 'categoria': categoria, 'descripcion': descripcion})

    def eliminar(self, client, foro_id):
        return client.post('/admin/foros', data={'accion': 'eliminar', 'foro_id': foro_id})


class VerGestionDeForos(ForosBase):
    def test_la_pagina_abre_para_el_admin_con_la_lista(self):
        html = self.cliente(ADMIN).get('/admin/foros').get_data(as_text=True)
        self.assertIn('Gestión de foros', html)
        self.assertIn('Cálculo III', html)
        self.assertIn('Vida Universitaria', html)

    def test_el_panel_enlaza_a_gestion_de_foros(self):
        html = self.cliente(ADMIN).get('/admin').get_data(as_text=True)
        self.assertIn('href="/admin/foros"', html)


class CrearForo(ForosBase):
    """Escenario: Crear un foro."""

    def test_se_crea_y_se_ve_el_mensaje(self):
        client = self.cliente(ADMIN)
        respuesta = self.crear(client, 'Física II', 'academico', 'Dudas de Física II')
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.headers['Location'].endswith('/admin/foros'))
        self.assertIn('Foro creado.', self.mensajes_flash(client))
        foro = self.conexion().execute("SELECT * FROM foros WHERE nombre = 'Física II'").fetchone()
        self.assertEqual(foro['categoria'], 'academico')
        self.assertEqual(foro['descripcion'], 'Dudas de Física II')
        self.assertEqual(foro['creado_por'], ADMIN)

    def test_aparece_en_la_lista_de_los_estudiantes(self):
        self.crear(self.cliente(ADMIN), 'Física II')
        html = self.cliente(ESTUDIANTE).get('/foros').get_data(as_text=True)
        self.assertIn('Física II', html)

    def test_el_nombre_se_guarda_sin_espacios_sobrantes(self):
        self.crear(self.cliente(ADMIN), '   Física II  ')
        self.assertEqual(self.contar("SELECT COUNT(*) FROM foros WHERE nombre = 'Física II'"), 1)


class CrearForoRepetido(ForosBase):
    """Escenario: Crear un foro con un nombre que ya existe."""

    def test_se_ve_el_mensaje_y_no_se_crea_otro(self):
        client = self.cliente(ADMIN)
        self.crear(client, 'Física II')
        self.crear(client, 'Física II')
        self.assertIn('Ya existe un foro con ese nombre.', self.mensajes_flash(client))
        self.assertEqual(self.contar("SELECT COUNT(*) FROM foros WHERE nombre = 'Física II'"), 1)

    def test_mayusculas_y_tildes_en_mayuscula_cuentan_como_repetido(self):
        # «CÁLCULO III» es el mismo foro que «Cálculo III» para quien lo lee.
        error = foros.crear_foro(self.conexion(), 'CÁLCULO III', '', 'matematicas', ADMIN)
        self.assertEqual(error, 'Ya existe un foro con ese nombre.')
        self.assertEqual(self.contar("SELECT COUNT(*) FROM foros"), 2)


class ValidacionesAlCrear(ForosBase):
    def test_sin_nombre_no_se_crea(self):
        client = self.cliente(ADMIN)
        self.crear(client, '   ')
        self.assertIn('El nombre del foro es obligatorio.', self.mensajes_flash(client))
        self.assertEqual(self.contar("SELECT COUNT(*) FROM foros"), 2)

    def test_un_nombre_de_mas_de_80_caracteres_se_rechaza(self):
        error = foros.crear_foro(self.conexion(), 'x' * 81, '', 'otro', ADMIN)
        self.assertEqual(error, 'El nombre no puede tener más de 80 caracteres.')

    def test_una_descripcion_de_mas_de_200_caracteres_se_rechaza(self):
        error = foros.crear_foro(self.conexion(), 'Física II', 'x' * 201, 'otro', ADMIN)
        self.assertEqual(error, 'La descripción no puede tener más de 200 caracteres.')

    def test_una_categoria_inventada_se_rechaza(self):
        client = self.cliente(ADMIN)
        self.crear(client, 'Física II', 'inventada')
        self.assertIn('Categoría no válida.', self.mensajes_flash(client))
        self.assertEqual(self.contar("SELECT COUNT(*) FROM foros"), 2)

    def test_una_accion_inventada_se_rechaza(self):
        client = self.cliente(ADMIN)
        client.post('/admin/foros', data={'accion': 'renombrar', 'foro_id': FORO_CALCULO})
        self.assertIn('Acción no válida.', self.mensajes_flash(client))


class EliminarForo(ForosBase):
    """Escenario: Eliminar un foro."""

    def test_se_elimina_y_se_ve_el_mensaje(self):
        client = self.cliente(ADMIN)
        respuesta = self.eliminar(client, FORO_CALCULO)
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('Foro eliminado.', self.mensajes_flash(client))
        self.assertEqual(self.contar("SELECT COUNT(*) FROM foros WHERE id = ?", FORO_CALCULO), 0)

    def test_se_borran_sus_preguntas_respuestas_y_votos(self):
        self.eliminar(self.cliente(ADMIN), FORO_CALCULO)
        # Solo queda el contenido del otro foro: 1 pregunta, 1 respuesta, 1 voto.
        self.assertEqual(self.contar("SELECT COUNT(*) FROM preguntas_foro"), 1)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM preguntas_foro WHERE foro_id = ?", FORO_OTRO), 1)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM respuestas_foro"), 1)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM votos_respuesta"), 1)

    def test_deja_de_aparecer_para_los_estudiantes(self):
        self.eliminar(self.cliente(ADMIN), FORO_CALCULO)
        estudiante = self.cliente(ESTUDIANTE)
        self.assertNotIn('Cálculo III', estudiante.get('/foros').get_data(as_text=True))
        respuesta = estudiante.get(f'/foros/{FORO_CALCULO}')
        self.assertEqual(respuesta.status_code, 302)  # "Foro no encontrado."

    def test_un_foro_que_no_existe_da_mensaje(self):
        client = self.cliente(ADMIN)
        self.eliminar(client, 999)
        self.assertIn('El foro no existe.', self.mensajes_flash(client))
        self.assertEqual(self.contar("SELECT COUNT(*) FROM foros"), 2)


class SoloElAdministrador(ForosBase):
    """Estudiantes, moderadores y visitantes no pueden ver ni cambiar los foros desde el panel."""

    def assert_acceso_denegado(self, user_id):
        client = self.cliente(user_id)
        for respuesta in (client.get('/admin/foros'),
                          self.crear(client, 'Física II'),
                          self.eliminar(client, FORO_CALCULO)):
            self.assertEqual(respuesta.status_code, 302)
            self.assertTrue(respuesta.headers['Location'].endswith('/feed'))
        self.assertEqual(self.contar("SELECT COUNT(*) FROM foros"), 2)

    def test_estudiante_no_entra(self):
        self.assert_acceso_denegado(ESTUDIANTE)

    def test_moderador_no_entra(self):
        self.assert_acceso_denegado(MODERADOR)

    def test_sin_sesion_va_al_login(self):
        client = self.cliente()
        for respuesta in (client.get('/admin/foros'), self.crear(client, 'Física II')):
            self.assertEqual(respuesta.status_code, 302)
            self.assertIn('/login', respuesta.headers['Location'])
        self.assertEqual(self.contar("SELECT COUNT(*) FROM foros"), 2)


if __name__ == '__main__':
    unittest.main()
