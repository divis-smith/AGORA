"""
Pruebas del issue #33: el administrador ve las estadísticas de la plataforma (RF-37).
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

ADMIN, MODERADOR, ANA, BETO, CARLA = 1, 2, 3, 4, 5

ESQUEMA = """
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, correo TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL DEFAULT 'x', carrera TEXT DEFAULT 'S', universidad TEXT DEFAULT 'U',
    bio TEXT, avatar_url TEXT, rol TEXT NOT NULL DEFAULT 'estudiante',
    activo INTEGER NOT NULL DEFAULT 1, creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE publicaciones (
    id INTEGER PRIMARY KEY, autor_id INTEGER NOT NULL, titulo TEXT NOT NULL DEFAULT 't',
    contenido TEXT NOT NULL DEFAULT 'c', categoria TEXT NOT NULL DEFAULT 'general',
    estado TEXT NOT NULL DEFAULT 'publicado', es_anonimo INTEGER NOT NULL DEFAULT 0
);
-- Solo para que /admin cargue sus totales.
CREATE TABLE reportes (id INTEGER PRIMARY KEY, estado TEXT NOT NULL DEFAULT 'enviado');
CREATE TABLE eventos (id INTEGER PRIMARY KEY, fecha DATE NOT NULL);
"""

# Todos los usuarios base se registraron hace un mes, para que no cuenten en los últimos 7 días.
USUARIOS = [
    (ADMIN, 'Admin', 'admin'),
    (MODERADOR, 'Mod', 'moderador'),
    (ANA, 'Ana', 'estudiante'),
    (BETO, 'Beto', 'estudiante'),
    (CARLA, 'Carla', 'estudiante'),
]


class EstadisticasBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_original = agora.DB
        agora.DB = os.path.join(self.tmp.name, 'test.db')
        agora.app.config['TESTING'] = True

        conn = sqlite3.connect(agora.DB)
        conn.executescript(ESQUEMA)
        conn.executemany(
            "INSERT INTO usuarios (id, nombre, correo, rol, creado_en) "
            "VALUES (?, ?, ?, ?, datetime('now', '-30 day'))",
            [(i, n, f'{i}@test.edu', r) for i, n, r in USUARIOS],
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

    def publicar(self, autor_id, categoria='general', estado='publicado', es_anonimo=0, veces=1):
        for _ in range(veces):
            self.ejecutar(
                "INSERT INTO publicaciones (autor_id, categoria, estado, es_anonimo) VALUES (?, ?, ?, ?)",
                autor_id, categoria, estado, es_anonimo,
            )

    def registrar(self, nombre, hace_dias):
        """Crea un usuario registrado hace `hace_dias` días."""
        self.ejecutar(
            "INSERT INTO usuarios (nombre, correo, creado_en) VALUES (?, ?, datetime('now', ?))",
            nombre, f'{nombre}@test.edu', f'-{hace_dias} day',
        )

    def consultar(self, funcion):
        conn = agora.get_db()
        try:
            return [dict(fila) for fila in funcion(conn)]
        finally:
            conn.close()

    def html(self, user_id=ADMIN):
        respuesta = self.cliente(user_id).get('/admin/estadisticas')
        self.assertEqual(respuesta.status_code, 200)
        return respuesta.get_data(as_text=True)

    def seccion(self, html, titulo):
        """Devuelve el HTML de la tarjeta cuyo título es `titulo`."""
        inicio = html.index(f'stat-card-titulo">{titulo}')
        fin = html.find('class="stat-card ', inicio + 1)
        return html[inicio:fin if fin != -1 else None]

    def mensajes_flash(self, client):
        with client.session_transaction() as s:
            return [mensaje for _, mensaje in s.get('_flashes', [])]


class VerLasEstadisticas(EstadisticasBase):
    """Escenario: Ver las estadísticas."""

    def test_el_panel_enlaza_a_estadisticas(self):
        respuesta = self.cliente(ADMIN).get('/admin')
        html = respuesta.get_data(as_text=True)
        self.assertIn('href="/admin/estadisticas"', html)
        self.assertNotIn('Próximamente', html)

    def test_muestra_las_tres_secciones_sin_error(self):
        html = self.html()
        for titulo in ('Posts por categoría', 'Top publicadores', 'Nuevos usuarios — últimos 7 días'):
            self.assertIn(titulo, html)

    def test_muestra_los_valores_de_la_base(self):
        self.publicar(ANA, 'academico', veces=3)
        self.publicar(BETO, 'meme')
        self.registrar('Nuevo', 0)
        html = self.html()

        categorias = self.seccion(html, 'Posts por categoría')
        self.assertRegex(categorias, r'(?s)academico</span>.*?bar-num">3<')
        self.assertRegex(categorias, r'(?s)meme</span>.*?bar-num">1<')

        top = self.seccion(html, 'Top publicadores')
        self.assertRegex(top, r'(?s)Ana</span>.*?bar-num">3<')
        self.assertRegex(top, r'(?s)Beto</span>.*?bar-num">1<')

        registros = self.seccion(html, 'Nuevos usuarios')
        self.assertEqual(re.findall(r'bar-num">(\d+)<', registros), ['1'])


class AnonimasNoCuentanParaElTop(EstadisticasBase):
    """Escenario: Las publicaciones anónimas no cuentan para el top."""

    def test_quien_solo_publica_anonimo_no_aparece(self):
        self.publicar(ANA, veces=2)
        self.publicar(CARLA, es_anonimo=1, veces=5)
        top = self.seccion(self.html(), 'Top publicadores')
        self.assertIn('Ana', top)
        self.assertNotIn('Carla', top)

    def test_las_anonimas_no_suman_al_conteo_de_quien_tambien_publica_con_nombre(self):
        self.publicar(ANA, veces=1)
        self.publicar(ANA, es_anonimo=1, veces=4)
        top = self.consultar(moderacion.top_publicadores)
        self.assertEqual(top, [{'nombre': 'Ana', 'n': 1}])

    def test_las_anonimas_si_cuentan_por_categoria(self):
        # La categoría no delata al autor, así que la publicación anónima sí suma ahí.
        self.publicar(CARLA, 'meme', es_anonimo=1, veces=2)
        categorias = self.consultar(moderacion.publicaciones_por_categoria)
        self.assertEqual(categorias, [{'categoria': 'meme', 'n': 2}])


class TodaviaNoHayDatos(EstadisticasBase):
    """Escenario: Todavía no hay datos."""

    def test_muestra_los_mensajes_de_vacio(self):
        html = self.html()
        self.assertIn('Sin datos aún.', html)
        self.assertIn('No hubo registros en los últimos 7 días.', html)

    def test_solo_borradores_y_eliminadas_cuenta_como_sin_datos(self):
        self.publicar(ANA, estado='borrador')
        self.publicar(BETO, estado='eliminado')
        self.assertEqual(self.consultar(moderacion.publicaciones_por_categoria), [])
        self.assertEqual(self.consultar(moderacion.top_publicadores), [])


class ConsultasDeEstadisticas(EstadisticasBase):
    """El servicio ordena y recorta como espera la plantilla."""

    def test_categorias_de_mayor_a_menor(self):
        self.publicar(ANA, 'meme')
        self.publicar(ANA, 'academico', veces=3)
        self.publicar(ANA, 'general', veces=2)
        categorias = self.consultar(moderacion.publicaciones_por_categoria)
        self.assertEqual([c['categoria'] for c in categorias], ['academico', 'general', 'meme'])

    def test_top_de_mayor_a_menor_con_empate_por_nombre(self):
        self.publicar(CARLA, veces=2)
        self.publicar(BETO, veces=2)
        self.publicar(ANA, veces=3)
        top = self.consultar(moderacion.top_publicadores)
        self.assertEqual([u['nombre'] for u in top], ['Ana', 'Beto', 'Carla'])

    def test_top_respeta_el_limite(self):
        for usuario_id in (ADMIN, MODERADOR, ANA, BETO, CARLA):
            self.publicar(usuario_id)
        top = self.consultar(lambda conn: moderacion.top_publicadores(conn, limite=3))
        self.assertEqual(len(top), 3)

    def test_registros_cuentan_hoy_y_los_seis_dias_anteriores(self):
        self.registrar('Hoy1', 0)
        self.registrar('Hoy2', 0)
        self.registrar('HaceSeis', 6)
        self.registrar('HaceSiete', 7)
        registros = self.consultar(moderacion.registros_ultimos_dias)
        # Dos días con registros, del más antiguo al más reciente; el de hace 7 días no entra.
        self.assertEqual([r['n'] for r in registros], [1, 2])
        self.assertLess(registros[0]['dia'], registros[1]['dia'])


class OtrosRolesNoEntran(EstadisticasBase):
    """Solo el administrador ve las estadísticas."""

    def assert_acceso_denegado(self, user_id):
        client = self.cliente(user_id)
        respuesta = client.get('/admin/estadisticas')
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta.headers['Location'].endswith('/feed'))
        self.assertIn('Acceso denegado.', self.mensajes_flash(client))

    def test_estudiante_ve_acceso_denegado(self):
        self.assert_acceso_denegado(ANA)

    def test_moderador_tampoco_entra(self):
        self.assert_acceso_denegado(MODERADOR)

    def test_sin_sesion_va_al_login(self):
        respuesta = self.cliente().get('/admin/estadisticas')
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login', respuesta.headers['Location'])


if __name__ == '__main__':
    unittest.main()
