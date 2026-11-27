# language: es
Característica: Agenda de un evento
  Como equipo de desarrollo
  Necesito que la agenda del evento se muestre como una lista de horas y actividades
  Para que los estudiantes la lean sin ver texto técnico

  # Referencia: Issue #40 y RNF-07 (relacionado: RF-26).

  Escenario: Evento con agenda
    Dado que el evento "Hackathon Univalle 2026 — retos de IA" tiene agenda
    Cuando abro su detalle
    Entonces veo cada actividad en su propia fila con su hora, por ejemplo "09:00" y "Apertura y registro"
    Y no veo llaves ni comillas del formato JSON

  Escenario: Evento sin agenda
    Dado que un evento no tiene agenda
    Cuando abro su detalle
    Entonces no veo la sección "Agenda"
