"""Consultas y reglas de foros, preguntas, respuestas y votos."""

from backend.nucleo.utilidades import con_tiempo_relativo, tiempo_relativo

TIPOS_PREGUNTA = ('pregunta', 'duda', 'apuntes', 'recurso', 'debate')

# (valor guardado, etiqueta) de las categorías que el administrador puede elegir.
CATEGORIAS_FORO = (
    ('campus', 'Campus'),
    ('matematicas', 'Matemáticas'),
    ('sistemas', 'Sistemas'),
    ('academico', 'Académico'),
    ('otro', 'Otro'),
)
MAX_NOMBRE_FORO = 80
MAX_DESCRIPCION_FORO = 200


def nombre_foro_en_uso(conn, nombre):
    """Indica si ya hay un foro con ese nombre, sin distinguir mayúsculas.

    Se compara en Python con casefold() porque el NOCASE de SQLite solo pasa a
    minúsculas las letras ASCII: para él «CÁLCULO» y «Cálculo» serían distintos.
    """
    buscado = nombre.casefold()
    return any(fila['nombre'].casefold() == buscado
               for fila in conn.execute("SELECT nombre FROM foros"))


def crear_foro(conn, nombre, descripcion, categoria, creado_por):
    """Crea un foro. Devuelve el mensaje de error, o None si lo creó."""
    nombre = (nombre or '').strip()
    descripcion = (descripcion or '').strip()
    if not nombre:
        return 'El nombre del foro es obligatorio.'
    if len(nombre) > MAX_NOMBRE_FORO:
        return f'El nombre no puede tener más de {MAX_NOMBRE_FORO} caracteres.'
    if len(descripcion) > MAX_DESCRIPCION_FORO:
        return f'La descripción no puede tener más de {MAX_DESCRIPCION_FORO} caracteres.'
    if categoria not in dict(CATEGORIAS_FORO):
        return 'Categoría no válida.'
    if nombre_foro_en_uso(conn, nombre):
        return 'Ya existe un foro con ese nombre.'
    conn.execute(
        "INSERT INTO foros (nombre, descripcion, categoria, creado_por) VALUES (?, ?, ?, ?)",
        (nombre, descripcion or None, categoria, creado_por),
    )
    conn.commit()
    return None


def eliminar_foro(conn, foro_id):
    """Elimina el foro con sus preguntas, respuestas y votos. Devuelve False si no existía.

    `abrir_conexion` no activa PRAGMA foreign_keys, así que el ON DELETE CASCADE
    del esquema no se aplica: se borra de las tablas hijas a la tabla padre.
    """
    if obtener_foro(conn, foro_id) is None:
        return False
    preguntas = "SELECT id FROM preguntas_foro WHERE foro_id = ?"
    respuestas = f"SELECT id FROM respuestas_foro WHERE pregunta_id IN ({preguntas})"
    with conn:  # una sola transacción: o se borra todo o nada
        conn.execute(f"DELETE FROM votos_respuesta WHERE respuesta_id IN ({respuestas})", (foro_id,))
        conn.execute(f"DELETE FROM respuestas_foro WHERE pregunta_id IN ({preguntas})", (foro_id,))
        conn.execute("DELETE FROM preguntas_foro WHERE foro_id = ?", (foro_id,))
        conn.execute("DELETE FROM foros WHERE id = ?", (foro_id,))
    return True


def listar_foros(conn):
    filas = conn.execute("""
        SELECT f.id, f.nombre, f.descripcion, f.categoria,
               (SELECT COUNT(*) FROM preguntas_foro pf WHERE pf.foro_id = f.id) AS total_preguntas
        FROM foros f ORDER BY total_preguntas DESC
    """).fetchall()
    return [dict(r) for r in filas]


def obtener_foro(conn, foro_id):
    return conn.execute("SELECT * FROM foros WHERE id = ?", (foro_id,)).fetchone()


def listar_preguntas(conn, foro_id):
    filas = conn.execute("""
        SELECT pf.id, pf.titulo, pf.contenido, pf.tipo, pf.es_anonimo, pf.creado_en,
               u.nombre AS autor_nombre,
               (SELECT COUNT(*) FROM respuestas_foro rf WHERE rf.pregunta_id = pf.id) AS total_respuestas
        FROM preguntas_foro pf
        JOIN usuarios u ON u.id = pf.autor_id
        WHERE pf.foro_id = ? ORDER BY pf.creado_en DESC
    """, (foro_id,)).fetchall()
    return con_tiempo_relativo(filas)


def crear_pregunta(conn, foro_id, autor_id, titulo, contenido, tipo, es_anonimo):
    conn.execute("""
        INSERT INTO preguntas_foro (foro_id, autor_id, titulo, contenido, tipo, es_anonimo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (foro_id, autor_id, titulo, contenido, tipo, es_anonimo))
    conn.commit()


def obtener_pregunta(conn, pregunta_id, foro_id):
    """Devuelve una pregunta del foro con el nombre de su autor, o None."""
    fila = conn.execute("""
        SELECT pf.*, u.nombre AS autor_nombre
        FROM preguntas_foro pf
        JOIN usuarios u ON u.id = pf.autor_id
        WHERE pf.id = ? AND pf.foro_id = ?
    """, (pregunta_id, foro_id)).fetchone()
    if not fila:
        return None
    pregunta = dict(fila)
    pregunta['tiempo_relativo'] = tiempo_relativo(pregunta['creado_en'])
    return pregunta


def listar_respuestas(conn, pregunta_id, usuario_id):
    """Devuelve las respuestas con sus votos y el voto del usuario."""
    filas = conn.execute("""
        SELECT rf.id, rf.contenido, rf.es_anonimo, rf.aceptada, rf.creado_en,
               rf.autor_id, u.nombre AS autor_nombre,
               COALESCE((SELECT SUM(v.valor) FROM votos_respuesta v WHERE v.respuesta_id = rf.id), 0) AS votos,
               (SELECT v.valor FROM votos_respuesta v
                WHERE v.respuesta_id = rf.id AND v.usuario_id = ?) AS mi_voto
        FROM respuestas_foro rf
        JOIN usuarios u ON u.id = rf.autor_id
        WHERE rf.pregunta_id = ?
        ORDER BY rf.aceptada DESC, votos DESC, rf.creado_en ASC
    """, (usuario_id, pregunta_id)).fetchall()
    respuestas = con_tiempo_relativo(filas)
    for respuesta in respuestas:
        respuesta['mi_voto'] = respuesta['mi_voto'] or 0
    return respuestas


def crear_respuesta(conn, pregunta_id, autor_id, contenido, es_anonimo):
    conn.execute(
        "INSERT INTO respuestas_foro (pregunta_id, autor_id, contenido, es_anonimo) VALUES (?,?,?,?)",
        (pregunta_id, autor_id, contenido, es_anonimo),
    )
    conn.commit()


def obtener_autoria_pregunta(conn, pregunta_id):
    return conn.execute(
        "SELECT autor_id, foro_id FROM preguntas_foro WHERE id = ?", (pregunta_id,)
    ).fetchone()


def aceptar_respuesta(conn, pregunta_id, respuesta_id):
    """Marca una respuesta como la aceptada de su pregunta."""
    conn.execute("UPDATE respuestas_foro SET aceptada = 0 WHERE pregunta_id = ?", (pregunta_id,))
    conn.execute(
        "UPDATE respuestas_foro SET aceptada = 1 WHERE id = ? AND pregunta_id = ?",
        (respuesta_id, pregunta_id),
    )
    conn.commit()


def votar_respuesta(conn, respuesta_id, usuario_id, valor):
    """Aplica el voto: el mismo voto lo quita y el opuesto lo cambia. Devuelve (total, mi_voto)."""
    existente = conn.execute(
        "SELECT valor FROM votos_respuesta WHERE respuesta_id = ? AND usuario_id = ?",
        (respuesta_id, usuario_id),
    ).fetchone()

    if existente and existente['valor'] == valor:
        conn.execute(
            "DELETE FROM votos_respuesta WHERE respuesta_id = ? AND usuario_id = ?",
            (respuesta_id, usuario_id),
        )
        mi_voto = 0
    elif existente:
        conn.execute(
            "UPDATE votos_respuesta SET valor = ? WHERE respuesta_id = ? AND usuario_id = ?",
            (valor, respuesta_id, usuario_id),
        )
        mi_voto = valor
    else:
        conn.execute(
            "INSERT INTO votos_respuesta (respuesta_id, usuario_id, valor) VALUES (?,?,?)",
            (respuesta_id, usuario_id, valor),
        )
        mi_voto = valor

    conn.commit()
    total = conn.execute(
        "SELECT COALESCE(SUM(valor), 0) AS total FROM votos_respuesta WHERE respuesta_id = ?",
        (respuesta_id,),
    ).fetchone()['total']
    return total, mi_voto
