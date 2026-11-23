# language: es
Característica: Panel de administración
  Como administrador
  Quiero abrir el panel de administración y ver los totales de la plataforma
  Para saber cómo va Ágora y llegar a las herramientas de gestión

  # Referencia: Issue #18 y RF-37.
  # Pruebas automáticas: tests/test_panel_admin.py

  Escenario: El administrador abre el panel
    Dado que inicié sesión como administrador
    Cuando abro "Administración" desde el menú lateral
    Entonces veo los totales "Usuarios activos", "Publicaciones", "Eventos próximos" y "Reportes nuevos"
    Y veo enlaces a gestión de usuarios y a moderación
    Y la página no responde error

  Escenario: Un estudiante intenta entrar
    Dado que inicié sesión como estudiante
    Cuando intento abrir /admin
    Entonces veo el mensaje "Acceso denegado."
    Y soy llevado al feed
