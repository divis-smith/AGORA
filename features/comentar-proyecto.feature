# language: es
Característica: Comentarios en proyectos
  Como estudiante
  Quiero comentar un proyecto del portafolio
  Para dar retroalimentación a su autor

  # Referencia: Issue #35 y RF-14.

  Escenario: Comentar un proyecto
    Dado que estoy viendo el detalle de un proyecto
    Cuando escribo un comentario y pulso "Comentar"
    Entonces veo el mensaje "Comentario publicado."
    Y mi comentario aparece en la lista con mi nombre

  Escenario: Comentario vacío
    Dado que estoy viendo el detalle de un proyecto
    Cuando envío un comentario sin texto
    Entonces veo el mensaje "El comentario no puede estar vacío."
    Y no se guarda ningún comentario

  Escenario: Comentario demasiado largo
    Dado que estoy viendo el detalle de un proyecto
    Cuando envío un comentario de más de 1000 caracteres
    Entonces veo el mensaje "El comentario no puede superar 1000 caracteres."
    Y no se guarda ningún comentario
