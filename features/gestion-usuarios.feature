# language: es
Característica: Gestión de usuarios y roles
  Como administrador
  Quiero buscar usuarios por nombre o correo y cambiar su rol
  Para nombrar moderadores sin tocar la base de datos

  # Referencia: Issue #19 y RF-38.
  # Pruebas automáticas: tests/test_gestion_usuarios.py

  Escenario: Buscar un usuario
    Dado que soy administrador y estoy en "Gestión de usuarios"
    Cuando busco "vale"
    Entonces veo solo los usuarios cuyo nombre o correo contiene "vale"

  Escenario: Cambiar el rol de un estudiante a moderador
    Dado que soy administrador y veo a un estudiante en la lista
    Cuando elijo el rol "Moderador" y pulso "Cambiar"
    Entonces veo el mensaje "Rol actualizado."
    Y esa persona puede abrir la pantalla de moderación

  Escenario: Intentar cambiar mi propio rol
    Dado que soy administrador
    Cuando intento cambiar mi propio rol
    Entonces veo el mensaje "No puedes cambiar tu propio rol."
    Y mi rol sigue siendo administrador
