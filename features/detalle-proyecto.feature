# language: es
Característica: Detalle de un proyecto
  Como estudiante
  Quiero abrir un proyecto del portafolio y ver todos sus datos
  Para conocerlo a fondo antes de aplaudirlo o comentarlo

  # Referencia: Issue #34 y RF-14.

  Escenario: Abrir un proyecto desde el portafolio
    Dado que inicié sesión como estudiante y estoy en el portafolio
    Cuando pulso el título de un proyecto
    Entonces veo su título, autor, descripción, tecnologías, estado, repositorio y demo
    Y veo cuántos aplausos tiene
    Y veo sus comentarios

  Escenario: Aplaudir desde el detalle
    Dado que estoy viendo el detalle de un proyecto que no he aplaudido
    Cuando pulso "Aplaudir"
    Entonces el contador de aplausos sube en uno
    Y el botón queda marcado como activo

  Escenario: Proyecto que no existe
    Dado que inicié sesión como estudiante
    Cuando abro el detalle de un proyecto que no existe
    Entonces veo el mensaje "Proyecto no encontrado."
    Y soy llevado al portafolio
