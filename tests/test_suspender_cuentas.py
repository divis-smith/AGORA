"""
Pruebas del issue #20: el administrador suspende y reactiva cuentas desde
/admin/usuarios (RF-36, RF-38).
Ejecutar desde la raíz del proyecto: python -m unittest discover -s tests -v

Reutilizan la base temporal de las pruebas de gestión de usuarios (#19).
"""

import os
import sys
import unittest

from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_gestion_usuarios import (  # noqa: E402
    ADMIN, MODERADOR, PEDRO, VALENTINA, GestionBase, agora, cuentas,
)

CLAVE_PEDRO = 'clave-de-pedro'


class EstadoBase(GestionBase):
    def setUp(self):
        super().setUp()
        # Pedro necesita una contraseña real para probar el inicio de sesión.
        conn = agora.get_db()
        conn.execute("UPDATE usuarios SET password = ? WHERE id = ?",
                     (generate_password_hash(CLAVE_PEDRO), PEDRO))
        conn.commit()
        conn.close()

    def activo(self, user_id):
        conn = agora.get_db()
        fila = conn.execute("SELECT activo FROM usuarios WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return bool(fila['activo'])

    def cambiar_estado(self, client, usuario_id, accion):
        return client.post(f'/admin/usuarios/{usuario_id}/estado', data={'accion': accion})

    def iniciar_sesion_pedro(self):
        client = agora.app.test_client()
        respuesta = client.post('/login', data={'correo': 'pedro@test.edu',
                                                'password': CLAVE_PEDRO})
        return client, respuesta


class SuspenderCuenta(EstadoBase):
    """Escenario: Suspender una cuenta."""

    def test_la_cuenta_queda_suspendida_y_se_ve_el_mensaje(self):
        client = self.cliente(ADMIN)
        respuesta = self.cambiar_estado(client, PEDRO, 'suspender')
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.headers['Location'].endswith('/admin/usuarios'))
        self.assertIn('Cuenta suspendida.', self.mensajes_flash(client))
        self.assertFalse(self.activo(PEDRO))

    def test_la_lista_la_muestra_como_suspendida(self):
        client = self.cliente(ADMIN)
        self.cambiar_estado(client, PEDRO, 'suspender')
        html = client.get('/admin/usuarios?q=pedro').get_data(as_text=True)
        self.assertIn('Suspendido', html)
        self.assertIn('Activar', html)

    def test_ya_no_puede_iniciar_sesion(self):
        self.cambiar_estado(self.cliente(ADMIN), PEDRO, 'suspender')
        client, respuesta = self.iniciar_sesion_pedro()
        self.assertEqual(respuesta.status_code, 200)  # se queda en el login
        self.assertIn('Tu cuenta está suspendida', respuesta.get_data(as_text=True))
        with client.session_transaction() as s:
            self.assertNotIn('user_id', s)

    def test_su_sesion_abierta_se_cierra(self):
        pedro = self.cliente(PEDRO)
        self.cambiar_estado(self.cliente(ADMIN), PEDRO, 'suspender')
        respuesta = pedro.get('/feed')
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login', respuesta.headers['Location'])


class ReactivarCuenta(EstadoBase):
    """Escenario: Reactivar una cuenta."""

    def setUp(self):
        super().setUp()
        self.cambiar_estado(self.cliente(ADMIN), PEDRO, 'suspender')

    def test_la_cuenta_vuelve_a_estar_activa(self):
        client = self.cliente(ADMIN)
        self.cambiar_estado(client, PEDRO, 'activar')
        self.assertIn('Cuenta activada.', self.mensajes_flash(client))
        self.assertTrue(self.activo(PEDRO))

    def test_puede_volver_a_iniciar_sesion(self):
        self.cambiar_estado(self.cliente(ADMIN), PEDRO, 'activar')
        client, respuesta = self.iniciar_sesion_pedro()
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.headers['Location'].endswith('/feed'))
        with client.session_transaction() as s:
            self.assertEqual(s['user_id'], PEDRO)


class SuspenderMiPropiaCuenta(EstadoBase):
    """Escenario: Suspender mi propia cuenta."""

    def test_se_ve_el_mensaje_y_sigo_activo(self):
        client = self.cliente(ADMIN)
        self.cambiar_estado(client, ADMIN, 'suspender')
        self.assertIn('No puedes suspender tu propia cuenta.', self.mensajes_flash(client))
        self.assertTrue(self.activo(ADMIN))

    def test_el_servicio_tambien_lo_impide(self):
        error = cuentas.cambiar_activo(self.conexion(), ADMIN, ADMIN, False)
        self.assertEqual(error, 'No puedes suspender tu propia cuenta.')
        self.assertTrue(self.activo(ADMIN))


class CasosBorde(EstadoBase):
    def test_una_accion_inventada_se_rechaza(self):
        client = self.cliente(ADMIN)
        self.cambiar_estado(client, PEDRO, 'borrar')
        self.assertIn('Acción no válida.', self.mensajes_flash(client))
        self.assertTrue(self.activo(PEDRO))

    def test_un_usuario_que_no_existe_da_mensaje(self):
        client = self.cliente(ADMIN)
        self.cambiar_estado(client, 999, 'suspender')
        self.assertIn('El usuario no existe.', self.mensajes_flash(client))


class SoloElAdministradorCambiaEstados(EstadoBase):
    """Estudiantes, moderadores y visitantes no pueden suspender desde el panel."""

    def assert_acceso_denegado(self, user_id):
        client = self.cliente(user_id)
        respuesta = self.cambiar_estado(client, PEDRO, 'suspender')
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.headers['Location'].endswith('/feed'))
        self.assertTrue(self.activo(PEDRO))

    def test_estudiante_no_puede(self):
        self.assert_acceso_denegado(VALENTINA)

    def test_moderador_no_puede(self):
        self.assert_acceso_denegado(MODERADOR)

    def test_sin_sesion_va_al_login(self):
        respuesta = self.cambiar_estado(self.cliente(), PEDRO, 'suspender')
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login', respuesta.headers['Location'])
        self.assertTrue(self.activo(PEDRO))


if __name__ == '__main__':
    unittest.main()
