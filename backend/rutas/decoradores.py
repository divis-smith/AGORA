"""Decoradores de control de acceso compartidos por los Blueprints."""

from functools import wraps

from flask import flash, redirect, session, url_for

from backend.servicios import cuentas


def login_required(vista):
    """Redirige al inicio de sesión si no hay una sesión activa."""
    @wraps(vista)
    def decorada(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('autenticacion.login'))
        return vista(*args, **kwargs)
    return decorada


def _crear_rol_required(get_db, roles_permitidos, mensaje):
    """Crea un decorador que solo deja pasar a los roles indicados.

    El rol se lee de la base en cada petición y no de la sesión, para que un cambio
    de rol o una suspensión tengan efecto sin esperar a que el usuario cierre sesión.
    """
    def rol_required(vista):
        @wraps(vista)
        def decorada(*args, **kwargs):
            if not session.get('user_id'):
                return redirect(url_for('autenticacion.login'))
            conn = get_db()
            usuario = cuentas.obtener_rol(conn, session['user_id'])
            conn.close()
            if not usuario or usuario['rol'] not in roles_permitidos:
                flash(mensaje, 'error')
                return redirect(url_for('publicaciones.feed'))
            return vista(*args, **kwargs)
        return decorada
    return rol_required


def crear_moderador_required(get_db):
    """Crea el decorador que limita una vista a moderadores y administradores."""
    return _crear_rol_required(
        get_db, ('moderador', 'admin'), 'No tienes permisos para acceder a esta sección.'
    )


def crear_admin_required(get_db):
    """Crea el decorador que limita una vista a administradores."""
    return _crear_rol_required(get_db, ('admin',), 'Acceso denegado.')
