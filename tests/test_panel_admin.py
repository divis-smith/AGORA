"""
Pruebas del issue #18: el administrador abre el panel de administración (RF-37).
Ejecutar desde la raíz del proyecto: python -m unittest discover -s tests -v

Usan una base de datos temporal; no tocan agora.db.
"""

import os
import re
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend import aplicacion as agora  # noqa: E402
from backend.servicios import moderacion  # noqa: E402

ADMIN, MODERADOR, ESTUDIANTE, SUSPENDIDO = 1, 2, 3, 4

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
CREATE TABLE reportes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, reportado_por INTEGER NOT NULL, tipo TEXT NOT NULL,
    referencia_id INTEGER NOT NULL, motivo TEXT NOT NULL, descripcion TEXT,
    estado TEXT NOT NULL DEFAULT 'enviado', revisado_por INTEGER, resolucion TEXT,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP, resuelto_en DATETIME
);
CREATE TABLE eventos (id INTEGER PRIMARY KEY, fecha DATE NOT NULL);
"""

USUARIOS = [
    (ADMIN, 'Admin', 'admin', 1),
    (MODERADOR, 'Mod', 'moderador', 1),
    (ESTUDIANTE, 'Ana', 'estudiante', 1),
    (SUSPENDIDO, 'Beto', 'estudiante', 0),
]


class PanelBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_original = agora.DB
        agora.DB = os.path.join(self.tmp.name, 'test.db')
        agora.app.config['TESTING'] = True

        conn = sqlite3.connect(agora.DB)
        conn.executescript(ESQUEMA)
        conn.executemany(
            "INSERT INTO usuarios (id, nombre, correo, rol, activo) VALUES (?, ?, ?, ?, ?)",
            [(i, n, f'{i}@test.edu', r, a) for i, n, r, a in USUARIOS],
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        agora.DB = self.db_original
        self.tmp.cleanup()

    def cliente(self, user_id=None):
        """Devuelve un cliente con la sesión de `user_id` (o sin sesión si es None)."""
        client = agora.app.test_client()
        if user_id is None:
            return client
        conn = agora.get_db()
        usuario = conn.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        with client.session_transaction() as s:
            s.update(user_id=usuario['id'], nombre=usuario['nombre'], carrera=usuario['carrera'],
                     universidad=usuario['universidad'], rol=usuario['rol'])
        return client

    def ejecutar(self, sql, *params):
        conn = agora.get_db()
        conn.execute(sql, params)
        conn.commit()
        conn.close()

    def cargar_datos(self):
        """Mezcla filas que cuentan con filas que no deben contar en el panel."""
        for estado in ('publicado', 'publicado', 'borrador'):
            self.ejecutar(
                "INSERT INTO publicaciones (autor_id, titulo, contenido, estado) VALUES (?, 't', 'c', ?)",
                ESTUDIANTE, estado,
            )
        for desfase in ('+0 day', '+7 day', '-1 day'):
            self.ejecutar("INSERT INTO eventos (fecha) VALUES (date('now', ?))", desfase)
        for estado in ('enviado', 'en_revision', 'resuelto'):
            self.ejecutar(
                "INSERT INTO reportes (reportado_por, tipo, referencia_id, motivo, estado) "
                "VALUES (?, 'usuario', ?, 'm', ?)",
                ESTUDIANTE, SUSPENDIDO, estado,
            )

    def mensajes_flash(self, client):
        with client.session_transaction() as s:
            return [mensaje for _, mensaje in s.get('_flashes', [])]


class AdministradorAbreElPanel(PanelBase):
    """Escenario: El administrador abre el panel."""

    def test_la_pagina_no_responde_error(self):
        respuesta = self.cliente(ADMIN).get('/admin')
        self.assertEqual(respuesta.status_code, 200)

    def test_muestra_los_cuatro_totales(self):
        html = self.cliente(ADMIN).get('/admin').get_data(as_text=True)
        for etiqueta in ('Usuarios activos', 'Publicaciones', 'Eventos próximos', 'Reportes nuevos'):
            self.assertIn(etiqueta, html)

    def test_los_totales_tienen_los_valores_de_la_base(self):
        self.cargar_datos()
        html = self.cliente(ADMIN).get('/admin').get_data(as_text=True)
        numeros = re.findall(r'class="stat-num[^"]*">\s*(\d+)\s*<', html)
        # Usuarios activos, publicaciones, eventos próximos y reportes nuevos, en ese orden.
        self.assertEqual(numeros, ['3', '2', '2', '2'])

    def test_enlaza_a_gestion_de_usuarios_y_a_moderacion(self):
        html = self.cliente(ADMIN).get('/admin').get_data(as_text=True)
        self.assertIn('Gestión de usuarios', html)
        self.assertIn('href="/moderacion"', html)

    def test_el_menu_lateral_tiene_el_enlace_al_panel(self):
        html = self.cliente(ADMIN).get('/admin').get_data(as_text=True)
        self.assertIn('href="/admin"', html)


class OtrosRolesNoEntran(PanelBase):
    """Escenario: Un estudiante intenta entrar (y lo mismo para moderador y sin sesión)."""

    def assert_acceso_denegado(self, user_id):
        client = self.cliente(user_id)
        respuesta = client.get('/admin')
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.headers['Location'].endswith('/feed'))
        self.assertIn('Acceso denegado.', self.mensajes_flash(client))

    def test_estudiante_ve_acceso_denegado_y_va_al_feed(self):
        self.assert_acceso_denegado(ESTUDIANTE)

    def test_moderador_tampoco_entra(self):
        self.assert_acceso_denegado(MODERADOR)

    def test_rol_cambiado_despues_de_iniciar_sesion_se_respeta(self):
        # La sesión dice admin, pero en la base ya lo bajaron a estudiante.
        client = self.cliente(ADMIN)
        self.ejecutar("UPDATE usuarios SET rol = 'estudiante' WHERE id = ?", ADMIN)
        respuesta = client.get('/admin')
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('Acceso denegado.', self.mensajes_flash(client))

    def test_sin_sesion_va_al_login(self):
        respuesta = self.cliente().get('/admin')
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login', respuesta.headers['Location'])


class TotalesDelPanel(PanelBase):
    """El servicio solo cuenta lo que el panel promete mostrar."""

    def test_cuenta_solo_lo_vigente(self):
        self.cargar_datos()
        conn = agora.get_db()
        totales = moderacion.totales_panel(conn)
        conn.close()
        self.assertEqual(totales, {
            'total_usuarios': 3,   # el suspendido no cuenta
            'total_posts': 2,      # el borrador no cuenta
            'total_eventos': 2,    # hoy y la próxima semana; el de ayer no
            'total_reportes': 2,   # enviado y en revisión; el resuelto no
        })

    def test_base_vacia_da_ceros(self):
        self.ejecutar("DELETE FROM usuarios")
        conn = agora.get_db()
        totales = moderacion.totales_panel(conn)
        conn.close()
        self.assertEqual(set(totales.values()), {0})


if __name__ == '__main__':
    unittest.main()
