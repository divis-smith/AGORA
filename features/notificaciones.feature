# language: es
Característica: Notificación por comentario
  Como estudiante
  Quiero que me avisen cuando alguien comenta mi publicación
  Para poder responder sin tener que revisar todo a mano

  # Referencia: Issue #9 y RF-40

  Escenario: Alguien comenta mi publicación
    Dado que publiqué algo
    Cuando otro estudiante comenta mi publicación
    Entonces recibo una notificación nueva que indica quién comentó

  Escenario: Comento mi propia publicación
    Dado que publiqué algo
    Cuando yo comento mi propia publicación
    Entonces no recibo ninguna notificación
