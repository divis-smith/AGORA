# language: es
Característica: Marcar una notificación como leída y eliminarla
  Como estudiante
  Quiero marcar mis notificaciones como leídas y eliminar las que ya no necesito
  Para saber qué me falta por revisar y mantener ordenada mi lista

  # Referencia: Issue #10, RF-41 y RF-42.

  Antecedentes:
    Dado que inicié sesión como estudiante y tengo notificaciones sin leer

  Escenario: Abrir la página de notificaciones
    Cuando entro a la página de notificaciones
    Entonces veo mis notificaciones sin leer resaltadas
    Y siguen sin leer hasta que yo las marque o las abra

  Escenario: Marcar una notificación como leída
    Cuando pulso el botón de marcar como leída en una notificación
    Entonces esa notificación deja de verse resaltada
    Y el contador de notificaciones del menú baja en uno
    Y las demás notificaciones siguen sin leer

  Escenario: Abrir una notificación
    Cuando pulso una notificación sin leer
    Entonces voy a la página a la que lleva
    Y esa notificación queda marcada como leída

  Escenario: Marcar todas como leídas
    Cuando pulso "Marcar todas como leídas"
    Entonces ninguna notificación se ve resaltada
    Y el contador de notificaciones del menú desaparece

  Escenario: Eliminar una notificación
    Cuando pulso el botón de eliminar en una notificación
    Entonces la notificación desaparece de la lista
    Y no vuelve a aparecer al recargar la página

  Escenario: Notificación de otro usuario
    Cuando intento marcar o eliminar una notificación que no es mía
    Entonces recibo un error de que la notificación no existe
    Y la notificación del otro usuario no cambia
