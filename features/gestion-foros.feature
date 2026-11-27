# language: es
Característica: Gestión de foros
  Como administrador
  Quiero crear y eliminar foros desde el panel
  Para gestionar las comunidades sin tocar los datos de demostración

  # Referencia: Issue #32 y RF-39.
  # Pruebas automáticas: tests/test_gestion_foros.py

  Escenario: Crear un foro
    Dado que soy administrador y estoy en "Gestión de foros"
    Cuando escribo el nombre "Física II", elijo una categoría y pulso "Crear foro"
    Entonces veo el mensaje "Foro creado."
    Y el foro aparece en la lista de foros de los estudiantes

  Escenario: Crear un foro con un nombre que ya existe
    Dado que ya existe el foro "Física II"
    Cuando intento crear otro foro llamado "Física II"
    Entonces veo el mensaje "Ya existe un foro con ese nombre."
    Y no se crea un segundo foro

  Escenario: Eliminar un foro
    Dado que soy administrador y veo un foro con preguntas en la lista
    Cuando pulso "Eliminar" y confirmo
    Entonces veo el mensaje "Foro eliminado."
    Y el foro y sus preguntas y respuestas dejan de aparecer
