"""Reglas de dominio compartidas por la moderación."""


TIPOS_REPORTE = ('publicacion', 'comentario', 'usuario')
ACCIONES_REPORTE = ('ignorar', 'eliminar', 'suspender')
ESTADOS_ABIERTOS = ('enviado', 'en_revision')
SQL_REPORTE_ABIERTO = "estado IN ('enviado', 'en_revision')"

CONSULTAS_USUARIO_REPORTADO = {
    'usuario': "SELECT id, rol FROM usuarios WHERE id = ?",
    'publicacion': """SELECT u.id, u.rol FROM publicaciones p
                      JOIN usuarios u ON u.id = p.autor_id WHERE p.id = ?""",
    'comentario': """SELECT u.id, u.rol FROM comentarios c
                      JOIN usuarios u ON u.id = c.autor_id WHERE c.id = ?""",
}


def obtener_usuario_reportado(conn, tipo, referencia_id):
    """Devuelve el responsable del reporte, o None si ya no existe."""
    consulta = CONSULTAS_USUARIO_REPORTADO.get(tipo)
    if not consulta:
        return None
    return conn.execute(consulta, (referencia_id,)).fetchone()


def motivo_para_no_suspender(objetivo, usuario_id, rol):
    """Explica por qué el usuario actual no puede suspender al objetivo."""
    if not objetivo:
        return 'El contenido reportado ya no existe; no se puede identificar a su autor.'
    if objetivo['id'] == usuario_id:
        return 'No puedes suspender tu propia cuenta.'
    if rol != 'admin' and objetivo['rol'] in ('admin', 'moderador'):
        return (
            'Solo un administrador puede suspender a un moderador, y un '
            'moderador no puede suspender a un administrador.'
        )
    return None


def listar_reportes_abiertos(conn):
    return conn.execute(f"""
        SELECT r.id, r.tipo, r.motivo, r.creado_en, r.estado,
               u.nombre AS reportador,
               r.referencia_id AS contenido_id
        FROM reportes r
        JOIN usuarios u ON u.id = r.reportado_por
        WHERE r.{SQL_REPORTE_ABIERTO}
        ORDER BY r.creado_en DESC
        LIMIT 50
    """).fetchall()


def contar_reportes_abiertos(conn):
    return conn.execute(
        f"SELECT COUNT(*) AS n FROM reportes WHERE {SQL_REPORTE_ABIERTO}"
    ).fetchone()['n']


def contar_reportes_resueltos(conn):
    return conn.execute("SELECT COUNT(*) AS n FROM reportes WHERE estado = 'resuelto'").fetchone()['n']


def contar_usuarios_activos(conn):
    return conn.execute("SELECT COUNT(*) AS n FROM usuarios WHERE activo = 1").fetchone()['n']


def existe_reporte_abierto(conn, usuario_id, tipo, referencia_id):
    return conn.execute(
        f"SELECT 1 FROM reportes WHERE reportado_por = ? AND tipo = ? AND referencia_id = ? AND {SQL_REPORTE_ABIERTO}",
        (usuario_id, tipo, referencia_id),
    ).fetchone() is not None


def crear_reporte(conn, usuario_id, tipo, referencia_id, motivo):
    conn.execute(
        "INSERT INTO reportes (reportado_por, tipo, referencia_id, motivo) VALUES (?, ?, ?, ?)",
        (usuario_id, tipo, referencia_id, motivo),
    )
    conn.commit()


def obtener_reporte(conn, reporte_id):
    return conn.execute("SELECT * FROM reportes WHERE id = ?", (reporte_id,)).fetchone()


def eliminar_contenido_reportado(conn, reporte):
    """Retira la publicación o el comentario señalado por el reporte."""
    if reporte['tipo'] == 'publicacion':
        conn.execute("UPDATE publicaciones SET estado = 'eliminado' WHERE id = ?", (reporte['referencia_id'],))
    elif reporte['tipo'] == 'comentario':
        conn.execute("DELETE FROM comentarios WHERE id = ?", (reporte['referencia_id'],))


def suspender_usuario(conn, usuario_id):
    conn.execute("UPDATE usuarios SET activo = 0 WHERE id = ?", (usuario_id,))


def cerrar_reporte(conn, reporte_id, revisor_id):
    """Marca el reporte como resuelto y confirma los cambios de la moderación."""
    conn.execute(
        "UPDATE reportes SET estado = 'resuelto', revisado_por = ? WHERE id = ?",
        (revisor_id, reporte_id),
    )
    conn.commit()


def listar_reportes_de_usuario(conn, usuario_id):
    return conn.execute(
        "SELECT * FROM reportes WHERE reportado_por = ? ORDER BY creado_en DESC",
        (usuario_id,),
    ).fetchall()


def totales_panel(conn):
    """Devuelve los contadores del panel de administración."""
    return {
        'total_usuarios': contar_usuarios_activos(conn),
        'total_posts': conn.execute(
            "SELECT COUNT(*) AS n FROM publicaciones WHERE estado = 'publicado'"
        ).fetchone()['n'],
        'total_reportes': contar_reportes_abiertos(conn),
        'total_eventos': conn.execute(
            "SELECT COUNT(*) AS n FROM eventos WHERE fecha >= date('now')"
        ).fetchone()['n'],
    }


def publicaciones_por_categoria(conn):
    """Cuenta las publicaciones vigentes de cada categoría, de mayor a menor.

    Las anónimas sí cuentan: la categoría no dice quién escribió.
    """
    return conn.execute("""
        SELECT categoria, COUNT(*) AS n FROM publicaciones
        WHERE estado = 'publicado'
        GROUP BY categoria ORDER BY n DESC, categoria
    """).fetchall()


def top_publicadores(conn, limite=5):
    """Devuelve los usuarios con más publicaciones vigentes con su nombre.

    Las anónimas no cuentan, para que el top no delate a sus autores (RNF-08).
    """
    return conn.execute("""
        SELECT u.nombre, COUNT(*) AS n FROM publicaciones p
        JOIN usuarios u ON u.id = p.autor_id
        WHERE p.estado = 'publicado' AND p.es_anonimo = 0
        GROUP BY u.id ORDER BY n DESC, u.nombre LIMIT ?
    """, (limite,)).fetchall()


def registros_ultimos_dias(conn, dias=7):
    """Cuenta los usuarios registrados por día en los últimos `dias` días, hoy incluido.

    Solo aparecen los días con registros, del más antiguo al más reciente.
    """
    return conn.execute("""
        SELECT date(creado_en) AS dia, COUNT(*) AS n FROM usuarios
        WHERE date(creado_en) >= date('now', ?)
        GROUP BY dia ORDER BY dia
    """, (f'-{dias - 1} day',)).fetchall()
