"""
Pruebas del issue #19: el administrador busca usuarios y cambia su rol (RF-38).
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
from backend.servicios import cuentas  # noqa: E402

ADMIN, MODERADOR, VALENTINA, PEDRO, ROSA = 1, 2, 3, 4, 5

ESQUEMA = """
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, correo TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL DEFAULT 'x', carrera TEXT DEFAULT 'S', universidad TEXT DEFAULT 'U',
    bio TEXT, avatar_url TEXT, rol TEXT NOT NULL DEFAULT 'estudiante',
    activo INTEGER NOT NULL DEFAULT 1, creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE reportes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, reportado_por INTEGER NOT NULL, tipo TEXT NOT NULL,
    referencia_id INTEGER NOT NULL, motivo TEXT NOT NULL, descripcion TEXT,
    estado TEXT NOT NULL DEFAULT 'enviado', revisado_por INTEGER, resolucion TEXT,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP, resuelto_en DATETIME
);
CREATE TABLE publicaciones (
    id INTEGER PRIMARY KEY, autor_id INTEGER NOT NULL, titulo TEXT NOT NULL,
    contenido TEXT NOT NULL, estado TEXT NOT NULL DEFAULT 'publicado'
);
CREATE TABLE eventos (id INTEGER PRIMARY KEY, fecha DATE NOT NULL);
"""

# (id, nombre, correo, rol)
USUARIOS = [
    (ADMIN, 'Admin', 'admin@test.edu', 'admin'),
    (MODERADOR, 'Mod', 'mod@test.edu', 'moderador'),
    (VALENTINA, 'Valentina Ruiz', 'vruiz@test.edu', 'estudiante'),
    (PEDRO, 'Pedro Gómez', 'pedro@test.edu', 'estudiante'),
    # El nombre no contiene "vale", pero el correo sí.
    (ROSA, 'Rosa Díaz', 'rosa.vale@test.edu', 'estudiante'),
]


class GestionBase(unittest.TestCase):
    def setUp(self):
        # Con addCleanup (y no tearDown) la carpeta se borra después de cerrar las
        # conexiones que abran las pruebas: las limpiezas corren en orden inverso.
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.addCleanup(setattr, agora, 'DB', agora.DB)
        agora.DB = os.path.join(tmp.name, 'test.db')
        agora.app.config['TESTING'] = True

        conn = sqlite3.connect(agora.DB)
        conn.executescript(ESQUEMA)
        conn.executemany("INSERT INTO usuarios (id, nombre, correo, rol) VALUES (?, ?, ?, ?)", USUARIOS)
        conn.commit()
        conn.close()

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

    def conexion(self):
        """Abre una conexión que se cierra sola al terminar la prueba, aunque falle."""
        conn = agora.get_db()
        self.addCleanup(conn.close)
        return conn

    def rol_de(self, user_id):
        conn = agora.get_db()
        fila = conn.execute("SELECT rol FROM usuarios WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return fila['rol']

    def mensajes_flash(self, client):
        with client.session_transaction() as s:
            return [mensaje for _, mensaje in s.get('_flashes', [])]

    def cambiar_rol(self, client, usuario_id, rol):
        return client.post(f'/admin/usuarios/{usuario_id}/rol', data={'rol': rol})


class BuscarUsuario(GestionBase):
    """Escenario: Buscar un usuario."""

    def test_la_pagina_abre_para_el_admin(self):
        respuesta = self.cliente(ADMIN).get('/admin/usuarios')
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('Gestión de usuarios', respuesta.get_data(as_text=True))

    def test_buscar_vale_muestra_solo_quienes_lo_contienen(self):
        html = self.cliente(ADMIN).get('/admin/usuarios?q=vale').get_data(as_text=True)
        self.assertIn('Valentina Ruiz', html)   # por el nombre, sin importar mayúsculas
        self.assertIn('Rosa Díaz', html)        # por el correo
        self.assertNotIn('Pedro Gómez', html)
        self.assertNotIn('mod@test.edu', html)

    def test_sin_busqueda_muestra_a_todos(self):
        usuarios = cuentas.buscar_usuarios(self.conexion(), '')
        self.assertEqual({u['id'] for u in usuarios}, {u[0] for u in USUARIOS})

    def test_los_comodines_de_like_se_buscan_como_texto(self):
        # "%" y "_" no deben funcionar como comodines y devolver a todos.
        conn = self.conexion()
        self.assertEqual(cuentas.buscar_usuarios(conn, '%'), [])
        self.assertEqual(cuentas.buscar_usuarios(conn, '_'), [])

    def test_el_panel_enlaza_a_gestion_de_usuarios(self):
        html = self.cliente(ADMIN).get('/admin').get_data(as_text=True)
        self.assertIn('href="/admin/usuarios"', html)


class CambiarRolAModerador(GestionBase):
    """Escenario: Cambiar el rol de un estudiante a moderador."""

    def test_el_rol_cambia_y_se_ve_el_mensaje(self):
        client = self.cliente(ADMIN)
        respuesta = self.cambiar_rol(client, PEDRO, 'moderador')
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.headers['Location'].endswith('/admin/usuarios'))
        self.assertIn('Rol actualizado.', self.mensajes_flash(client))
        self.assertEqual(self.rol_de(PEDRO), 'moderador')

    def test_el_nuevo_moderador_abre_moderacion_sin_cerrar_sesion(self):
        pedro = self.cliente(PEDRO)
        self.assertEqual(pedro.get('/moderacion').status_code, 302)  # antes no puede

        self.cambiar_rol(self.cliente(ADMIN), PEDRO, 'moderador')

        self.assertEqual(pedro.get('/moderacion').status_code, 200)  # misma sesión

    def test_un_rol_inventado_se_rechaza(self):
        client = self.cliente(ADMIN)
        self.cambiar_rol(client, PEDRO, 'superadmin')
        self.assertIn('Rol no válido.', self.mensajes_flash(client))
        self.assertEqual(self.rol_de(PEDRO), 'estudiante')

    def test_un_usuario_que_no_existe_da_mensaje(self):
        client = self.cliente(ADMIN)
        self.cambiar_rol(client, 999, 'moderador')
        self.assertIn('El usuario no existe.', self.mensajes_flash(client))


class CambiarMiPropioRol(GestionBase):
    """Escenario: Intentar cambiar mi propio rol."""

    def test_se_ve_el_mensaje_y_sigo_siendo_admin(self):
        client = self.cliente(ADMIN)
        self.cambiar_rol(client, ADMIN, 'estudiante')
        self.assertIn('No puedes cambiar tu propio rol.', self.mensajes_flash(client))
        self.assertEqual(self.rol_de(ADMIN), 'admin')

    def test_el_servicio_tambien_lo_impide(self):
        # La regla vive en el servicio, no solo en la ruta.
        error = cuentas.cambiar_rol(self.conexion(), ADMIN, ADMIN, 'moderador')
        self.assertEqual(error, 'No puedes cambiar tu propio rol.')
        self.assertEqual(self.rol_de(ADMIN), 'admin')


class SoloElAdministrador(GestionBase):
    """Estudiantes, moderadores y visitantes no pueden ver la lista ni cambiar roles."""

    def assert_acceso_denegado(self, user_id):
        client = self.cliente(user_id)
        for respuesta in (client.get('/admin/usuarios'),
                          self.cambiar_rol(client, PEDRO, 'admin')):
            self.assertEqual(respuesta.status_code, 302)
            self.assertTrue(respuesta.headers['Location'].endswith('/feed'))
        self.assertIn('Acceso denegado.', self.mensajes_flash(client))
        self.assertEqual(self.rol_de(PEDRO), 'estudiante')

    def test_estudiante_no_entra(self):
        self.assert_acceso_denegado(VALENTINA)

    def test_moderador_no_entra(self):
        self.assert_acceso_denegado(MODERADOR)

    def test_sin_sesion_va_al_login(self):
        client = self.cliente()
        for respuesta in (client.get('/admin/usuarios'),
                          self.cambiar_rol(client, PEDRO, 'admin')):
            self.assertEqual(respuesta.status_code, 302)
            self.assertIn('/login', respuesta.headers['Location'])
        self.assertEqual(self.rol_de(PEDRO), 'estudiante')


if __name__ == '__main__':
    unittest.main()
