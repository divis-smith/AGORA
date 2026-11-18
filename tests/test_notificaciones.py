"""
Pruebas del issue #10: marcar una notificación como leída y eliminarla (RF-41 y RF-42).
Ejecutar desde la raíz del proyecto: python -m unittest discover -s tests -v

Usan una base de datos temporal; no tocan agora.db.
"""

import os
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend import aplicacion as agora  # noqa: E402

DUENO, OTRO = 1, 2

ESQUEMA = """
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, correo TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL DEFAULT 'x', carrera TEXT DEFAULT 'S', universidad TEXT DEFAULT 'U',
    bio TEXT, avatar_url TEXT, rol TEXT NOT NULL DEFAULT 'estudiante',
    activo INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE notificaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT, usuario_id INTEGER NOT NULL, tipo TEXT NOT NULL,
    mensaje TEXT NOT NULL, leida INTEGER NOT NULL DEFAULT 0, url TEXT,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


class NotificacionesBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_original = agora.DB
        agora.DB = os.path.join(self.tmp.name, 'test.db')
        agora.app.config['TESTING'] = True

        conn = sqlite3.connect(agora.DB)
        conn.executescript(ESQUEMA)
        conn.executemany(
            "INSERT INTO usuarios (id, nombre, correo) VALUES (?, ?, ?)",
            [(DUENO, 'Dueño', 'dueno@test.edu'), (OTRO, 'Otro', 'otro@test.edu')],
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        agora.DB = self.db_original
        self.tmp.cleanup()

    def cliente(self, user_id):
        client = agora.app.test_client()
        with client.session_transaction() as s:
            s.update(user_id=user_id, nombre='N', carrera='S', universidad='U', rol='estudiante')
        return client

    def crear_notificacion(self, usuario_id, leida=0, mensaje='Alguien comentó tu publicación.'):
        conn = agora.get_db()
        cur = conn.execute(
            "INSERT INTO notificaciones (usuario_id, tipo, mensaje, leida, url) VALUES (?, 'comentario', ?, ?, '/feed')",
            (usuario_id, mensaje, leida),
        )
        conn.commit()
        notificacion_id = cur.lastrowid
        conn.close()
        return notificacion_id

    def notificacion(self, notificacion_id):
        conn = agora.get_db()
        fila = conn.execute("SELECT * FROM notificaciones WHERE id = ?", (notificacion_id,)).fetchone()
        conn.close()
        return fila

    def marcar(self, user_id, notificacion_id):
        return self.cliente(user_id).post(f'/notificaciones/{notificacion_id}/leida')

    def eliminar(self, user_id, notificacion_id):
        return self.cliente(user_id).post(f'/notificaciones/{notificacion_id}/eliminar')


class MarcarComoLeida(NotificacionesBase):
    def test_marca_solo_esa_notificacion(self):
        primera = self.crear_notificacion(DUENO)
        segunda = self.crear_notificacion(DUENO)
        respuesta = self.marcar(DUENO, primera)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.get_json(), {'ok': True, 'no_leidas': 1})
        self.assertEqual(self.notificacion(primera)['leida'], 1)
        self.assertEqual(self.notificacion(segunda)['leida'], 0)

    def test_marcar_una_ya_leida_no_falla(self):
        notificacion = self.crear_notificacion(DUENO, leida=1)
        respuesta = self.marcar(DUENO, notificacion)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(self.notificacion(notificacion)['leida'], 1)

    def test_no_puede_marcar_la_de_otro_usuario(self):
        ajena = self.crear_notificacion(OTRO)
        respuesta = self.marcar(DUENO, ajena)
        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(self.notificacion(ajena)['leida'], 0)

    def test_notificacion_inexistente(self):
        self.assertEqual(self.marcar(DUENO, 999).status_code, 404)

    def test_marcar_todas(self):
        propias = [self.crear_notificacion(DUENO) for _ in range(3)]
        ajena = self.crear_notificacion(OTRO)
        respuesta = self.cliente(DUENO).post('/notificaciones/leer-todas')
        self.assertEqual(respuesta.get_json(), {'ok': True, 'no_leidas': 0})
        for notificacion in propias:
            self.assertEqual(self.notificacion(notificacion)['leida'], 1)
        self.assertEqual(self.notificacion(ajena)['leida'], 0)

    def test_abrir_la_pagina_ya_no_marca_todas(self):
        notificacion = self.crear_notificacion(DUENO)
        self.assertEqual(self.cliente(DUENO).get('/notificaciones').status_code, 200)
        self.assertEqual(self.notificacion(notificacion)['leida'], 0)

    def test_sin_sesion_redirige_al_login(self):
        notificacion = self.crear_notificacion(DUENO)
        respuesta = agora.app.test_client().post(f'/notificaciones/{notificacion}/leida')
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(self.notificacion(notificacion)['leida'], 0)


class EliminarNotificacion(NotificacionesBase):
    def test_elimina_solo_esa_notificacion(self):
        borrar = self.crear_notificacion(DUENO)
        conservar = self.crear_notificacion(DUENO)
        respuesta = self.eliminar(DUENO, borrar)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.get_json(), {'ok': True, 'no_leidas': 1})
        self.assertIsNone(self.notificacion(borrar))
        self.assertIsNotNone(self.notificacion(conservar))

    def test_no_puede_eliminar_la_de_otro_usuario(self):
        ajena = self.crear_notificacion(OTRO)
        self.assertEqual(self.eliminar(DUENO, ajena).status_code, 404)
        self.assertIsNotNone(self.notificacion(ajena))

    def test_eliminar_dos_veces(self):
        notificacion = self.crear_notificacion(DUENO)
        self.eliminar(DUENO, notificacion)
        self.assertEqual(self.eliminar(DUENO, notificacion).status_code, 404)

    def test_la_eliminada_no_aparece_en_la_pagina(self):
        self.crear_notificacion(DUENO, mensaje='Esta se queda.')
        borrar = self.crear_notificacion(DUENO, mensaje='Esta se borra.')
        self.eliminar(DUENO, borrar)
        html = self.cliente(DUENO).get('/notificaciones').get_data(as_text=True)
        self.assertIn('Esta se queda.', html)
        self.assertNotIn('Esta se borra.', html)


class PantallaDeNotificaciones(NotificacionesBase):
    def html(self):
        return self.cliente(DUENO).get('/notificaciones').get_data(as_text=True)

    def test_no_leida_tiene_boton_de_marcar_y_eliminar(self):
        notificacion = self.crear_notificacion(DUENO)
        html = self.html()
        self.assertIn(f'data-marcar-leida="{notificacion}"', html)
        self.assertIn(f'data-eliminar-notificacion="{notificacion}"', html)
        self.assertIn('Marcar todas como leídas', html)

    def test_leida_solo_tiene_boton_de_eliminar(self):
        notificacion = self.crear_notificacion(DUENO, leida=1)
        html = self.html()
        self.assertNotIn(f'data-marcar-leida="{notificacion}"', html)
        self.assertIn(f'data-eliminar-notificacion="{notificacion}"', html)
        self.assertNotIn('Marcar todas como leídas', html)


if __name__ == '__main__':
    unittest.main()
