"""
Pruebas del issue #9 (RF-40): notificar al autor cuando comentan su publicación.
Ejecutar desde la raíz del proyecto: python -m unittest discover -s tests -v

Usan una base de datos temporal; no tocan agora.db.
"""

import os
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend import aplicacion as agora  # noqa: E402
from backend.servicios import publicaciones as servicio  # noqa: E402

AUTOR, COMENTARISTA = 1, 2
PUBLICACION = 10

ESQUEMA = """
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, correo TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL DEFAULT 'x', carrera TEXT DEFAULT 'S', universidad TEXT DEFAULT 'U',
    bio TEXT, avatar_url TEXT, rol TEXT NOT NULL DEFAULT 'estudiante',
    activo INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE publicaciones (
    id INTEGER PRIMARY KEY, autor_id INTEGER NOT NULL, titulo TEXT NOT NULL,
    contenido TEXT NOT NULL, estado TEXT NOT NULL DEFAULT 'publicado'
);
CREATE TABLE comentarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT, publicacion_id INTEGER NOT NULL,
    autor_id INTEGER NOT NULL, contenido TEXT NOT NULL
);
CREATE TABLE notificaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL, tipo TEXT NOT NULL,
    mensaje TEXT NOT NULL, leida INTEGER NOT NULL DEFAULT 0, url TEXT,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


class NotificacionComentarioBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_original = agora.DB
        agora.DB = os.path.join(self.tmp.name, 'test.db')
        agora.app.config['TESTING'] = True

        conn = sqlite3.connect(agora.DB)
        conn.executescript(ESQUEMA)
        conn.executemany(
            "INSERT INTO usuarios (id, nombre, correo) VALUES (?, ?, ?)",
            [(AUTOR, 'Autora', 'autora@test.edu'), (COMENTARISTA, 'Camilo', 'camilo@test.edu')],
        )
        conn.execute(
            "INSERT INTO publicaciones (id, autor_id, titulo, contenido) VALUES (?, ?, 't', 'c')",
            (PUBLICACION, AUTOR),
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        agora.DB = self.db_original
        self.tmp.cleanup()

    def cliente(self, user_id):
        client = agora.app.test_client()
        conn = agora.get_db()
        usuario = conn.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        with client.session_transaction() as s:
            s.update(user_id=usuario['id'], nombre=usuario['nombre'], carrera=usuario['carrera'],
                     universidad=usuario['universidad'], rol=usuario['rol'])
        return client

    def comentar(self, user_id, texto='Buen aporte', post_id=PUBLICACION):
        return self.cliente(user_id).post(
            f'/comentar/{post_id}', data={'contenido': texto},
        )

    def notificaciones(self, usuario_id):
        conn = agora.get_db()
        filas = conn.execute(
            "SELECT * FROM notificaciones WHERE usuario_id = ?", (usuario_id,)
        ).fetchall()
        conn.close()
        return filas

    def total(self, tabla):
        conn = agora.get_db()
        n = conn.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
        conn.close()
        return n


class NotificacionComentarioTest(NotificacionComentarioBase):
    def test_comentario_ajeno_notifica_al_autor_e_indica_quien_comento(self):
        self.comentar(COMENTARISTA)

        notificaciones = self.notificaciones(AUTOR)
        self.assertEqual(len(notificaciones), 1)
        self.assertEqual(notificaciones[0]['tipo'], 'comentario')
        self.assertIn('Camilo', notificaciones[0]['mensaje'])
        self.assertEqual(notificaciones[0]['leida'], 0)
        self.assertIn(f'/post/{PUBLICACION}', notificaciones[0]['url'])

    def test_comentar_la_propia_publicacion_no_notifica(self):
        self.comentar(AUTOR)

        self.assertEqual(self.notificaciones(AUTOR), [])

    def test_comentario_vacio_no_notifica(self):
        self.comentar(COMENTARISTA, texto='   ')

        self.assertEqual(self.notificaciones(AUTOR), [])

    def test_comentar_no_crea_notificaciones_para_el_comentarista(self):
        self.comentar(COMENTARISTA)

        self.assertEqual(self.notificaciones(COMENTARISTA), [])

    def test_comentar_publicacion_inexistente_no_guarda_nada(self):
        respuesta = self.comentar(COMENTARISTA, post_id=999)

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(self.total('comentarios'), 0)
        self.assertEqual(self.total('notificaciones'), 0)

    def test_servicio_lanza_error_si_la_publicacion_no_existe(self):
        conn = agora.get_db()
        try:
            with self.assertRaises(ValueError):
                servicio.comentar(conn, 999, COMENTARISTA, 'hola', '/post/999')
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM comentarios").fetchone()[0], 0)
        finally:
            conn.close()


class AvisoEnVivoComentarioTest(NotificacionComentarioBase):
    def test_emite_el_aviso_a_la_sala_del_autor(self):
        with mock.patch.object(agora.socketio, 'emit') as emit:
            self.comentar(COMENTARISTA)

        emit.assert_called_once_with(
            'notificacion',
            {'mensaje': 'Camilo comentó tu publicación.', 'tipo': 'comentario',
             'url': f'/post/{PUBLICACION}'},
            room=f'user_{AUTOR}',
        )

    def test_no_emite_nada_si_comenta_su_propia_publicacion(self):
        with mock.patch.object(agora.socketio, 'emit') as emit:
            self.comentar(AUTOR)

        emit.assert_not_called()

    def test_si_falla_el_aviso_el_comentario_y_la_notificacion_quedan_guardados(self):
        with mock.patch.object(agora.socketio, 'emit', side_effect=RuntimeError('socket caído')):
            respuesta = self.comentar(COMENTARISTA)

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(self.total('comentarios'), 1)
        self.assertEqual(len(self.notificaciones(AUTOR)), 1)


if __name__ == '__main__':
    unittest.main()
