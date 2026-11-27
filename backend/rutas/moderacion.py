"""Rutas de reportes, moderación y panel de administración."""

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from backend.rutas.decoradores import crear_admin_required, crear_moderador_required, login_required
from backend.servicios import cuentas, foros
from backend.servicios import moderacion as servicio

# accion del formulario de /admin/usuarios -> (nuevo valor de activo, mensaje)
ACCIONES_ESTADO = {
    'suspender': (False, 'Cuenta suspendida.'),
    'activar': (True, 'Cuenta activada.'),
}


def crear_blueprint(get_db):
    """Crea el Blueprint de moderación."""
    blueprint = Blueprint('moderacion', __name__)
    moderador_required = crear_moderador_required(get_db)
    admin_required = crear_admin_required(get_db)

    @blueprint.route('/moderacion')
    @login_required
    @moderador_required
    def moderacion():
        conn = get_db()
        reportes = servicio.listar_reportes_abiertos(conn)
        total_pendientes = servicio.contar_reportes_abiertos(conn)
        total_resueltos = servicio.contar_reportes_resueltos(conn)
        total_usuarios = servicio.contar_usuarios_activos(conn)
        conn.close()
        return render_template('moderacion/moderacion.html',
                               reportes=reportes,
                               total_pendientes=total_pendientes,
                               total_resueltos=total_resueltos,
                               total_usuarios=total_usuarios,
                               pagina_activa='moderacion')

    @blueprint.route('/reporte/nuevo', methods=['POST'])
    @login_required
    def crear_reporte():
        """Cualquier usuario puede reportar contenido."""
        tipo = request.form.get('tipo', '')        # publicacion, comentario, usuario
        contenido_id = request.form.get('contenido_id', 0, type=int)
        motivo = request.form.get('motivo', '').strip()
        if tipo not in servicio.TIPOS_REPORTE:
            return jsonify({'ok': False, 'error': 'Tipo de reporte no válido'}), 400
        if not contenido_id or not motivo:
            return jsonify({'ok': False, 'error': 'Datos incompletos'}), 400
        conn = get_db()
        try:
            objetivo = servicio.obtener_usuario_reportado(conn, tipo, contenido_id)
            if not objetivo:
                return jsonify({'ok': False, 'error': 'El contenido reportado no existe.'}), 404
            if objetivo['id'] == session['user_id']:
                return jsonify({'ok': False, 'error': 'No puedes reportar tu propio contenido.'}), 400
            # Evitar reportes duplicados del mismo usuario
            if servicio.existe_reporte_abierto(conn, session['user_id'], tipo, contenido_id):
                return jsonify({'ok': False, 'error': 'Ya reportaste este contenido.'})
            servicio.crear_reporte(conn, session['user_id'], tipo, contenido_id, motivo)
            return jsonify({'ok': True})
        finally:
            conn.close()

    @blueprint.route('/moderacion/resolver/<int:reporte_id>', methods=['POST'])
    @login_required
    @moderador_required
    def resolver_reporte(reporte_id):
        accion = request.form.get('accion', 'ignorar')  # ignorar | eliminar | suspender
        if accion not in servicio.ACCIONES_REPORTE:
            flash('Acción no válida.', 'error')
            return redirect(url_for('moderacion.moderacion'))
        conn = get_db()
        try:
            reporte = servicio.obtener_reporte(conn, reporte_id)
            if not reporte:
                flash('Reporte no encontrado.', 'error')
                return redirect(url_for('moderacion.moderacion'))
            if reporte['estado'] not in servicio.ESTADOS_ABIERTOS:
                flash('Este reporte ya estaba cerrado.', 'error')
                return redirect(url_for('moderacion.moderacion'))
            if accion == 'eliminar' and reporte['tipo'] == 'usuario':
                flash('Un reporte de usuario no tiene contenido que eliminar.', 'error')
                return redirect(url_for('moderacion.moderacion'))
            if accion == 'eliminar':
                servicio.eliminar_contenido_reportado(conn, reporte)
            elif accion == 'suspender':
                objetivo = servicio.obtener_usuario_reportado(conn, reporte['tipo'], reporte['referencia_id'])
                error = servicio.motivo_para_no_suspender(
                    objetivo, session['user_id'], session.get('rol')
                )
                if error:
                    flash(error, 'error')
                    return redirect(url_for('moderacion.moderacion'))
                servicio.suspender_usuario(conn, objetivo['id'])
            servicio.cerrar_reporte(conn, reporte_id, session['user_id'])
            flash(f'Reporte #{reporte_id} resuelto ({accion}).', 'success')
        finally:
            conn.close()
        return redirect(url_for('moderacion.moderacion'))

    @blueprint.route('/reportes')
    @login_required
    def reportes():
        conn = get_db()
        mis_reportes = servicio.listar_reportes_de_usuario(conn, session['user_id'])
        conn.close()
        return render_template('moderacion/reportes.html', reportes=mis_reportes, pagina_activa='reportes')

    @blueprint.route('/admin')
    @login_required
    @admin_required
    def admin_panel():
        conn = get_db()
        stats = servicio.totales_panel(conn)
        conn.close()
        return render_template('moderacion/panel.html', stats=stats, pagina_activa='admin')

    @blueprint.route('/admin/foros', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_foros():
        conn = get_db()
        try:
            if request.method == 'POST':
                accion = request.form.get('accion', '')
                if accion == 'crear':
                    error = foros.crear_foro(conn, request.form.get('nombre'),
                                             request.form.get('descripcion'),
                                             request.form.get('categoria', ''), session['user_id'])
                    flash(error or 'Foro creado.', 'error' if error else 'success')
                elif accion == 'eliminar':
                    if foros.eliminar_foro(conn, request.form.get('foro_id', 0, type=int)):
                        flash('Foro eliminado.', 'success')
                    else:
                        flash('El foro no existe.', 'error')
                else:
                    flash('Acción no válida.', 'error')
                return redirect(url_for('moderacion.admin_foros'))
            lista = foros.listar_foros(conn)
        finally:
            conn.close()
        return render_template('moderacion/foros.html', foros=lista,
                               categorias=foros.CATEGORIAS_FORO, pagina_activa='admin')

    @blueprint.route('/admin/usuarios')
    @login_required
    @admin_required
    def admin_usuarios():
        q = request.args.get('q', '').strip()
        conn = get_db()
        usuarios = cuentas.buscar_usuarios(conn, q)
        conn.close()
        return render_template('moderacion/usuarios.html', usuarios=usuarios, q=q,
                               roles=cuentas.ROLES, pagina_activa='admin')

    @blueprint.route('/admin/usuarios/<int:usuario_id>/rol', methods=['POST'])
    @login_required
    @admin_required
    def admin_cambiar_rol(usuario_id):
        conn = get_db()
        error = cuentas.cambiar_rol(conn, session['user_id'], usuario_id, request.form.get('rol', ''))
        conn.close()
        if error:
            flash(error, 'error')
        else:
            flash('Rol actualizado.', 'success')
        return redirect(url_for('moderacion.admin_usuarios'))

    @blueprint.route('/admin/usuarios/<int:usuario_id>/estado', methods=['POST'])
    @login_required
    @admin_required
    def admin_cambiar_estado(usuario_id):
        accion = request.form.get('accion', '')
        if accion not in ACCIONES_ESTADO:
            flash('Acción no válida.', 'error')
            return redirect(url_for('moderacion.admin_usuarios'))
        activo, mensaje = ACCIONES_ESTADO[accion]
        conn = get_db()
        error = cuentas.cambiar_activo(conn, session['user_id'], usuario_id, activo)
        conn.close()
        flash(error or mensaje, 'error' if error else 'success')
        return redirect(url_for('moderacion.admin_usuarios'))

    return blueprint
