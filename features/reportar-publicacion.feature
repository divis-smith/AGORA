# language: es
Característica: Reportar una publicación
  Como estudiante
  Quiero reportar una publicación inapropiada
  Para que los moderadores la revisen

  # Referencia: Issue #6 y RF-32.

  Escenario: Reportar una publicación
    Dado que inicié sesión como estudiante y estoy viendo una publicación de otra persona
    Cuando pulso reportar, elijo un motivo y envío el reporte
    Entonces veo un mensaje de confirmación
    Y el reporte queda registrado con estado abierto

  Escenario: Reporte duplicado
    Dado que ya reporté esa publicación y mi reporte sigue abierto
    Cuando intento reportarla otra vez
    Entonces veo un mensaje que indica que ya la reporté
    Y no se crea un segundo reporte
