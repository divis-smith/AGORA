# language: es
Característica: Resolución visible de mis reportes
  Como estudiante
  Quiero ver cómo cerraron mi reporte
  Para saber si los moderadores actuaron o lo descartaron

  # Referencia: Issue #27 y RF-33, RF-35.

  Escenario: Ver mis reportes
    Dado que inicié sesión como estudiante y tengo un reporte abierto
    Cuando abro la pantalla de mis reportes
    Entonces veo el reporte con su estado actual

  Escenario: Sin reportes
    Dado que inicié sesión como estudiante y nunca he reportado nada
    Cuando abro la pantalla de mis reportes
    Entonces veo un mensaje que indica que no tengo reportes
    Y la pantalla no responde error

  Escenario: Llegar a mis reportes desde el menú 
    Dado que inicie seccion como estudiante
    Cuando selecciono "Mis reportes" en el menú
    Entonces soy dirigido a la pantala de mis reportes

  Escenario: El moderador ignora mi reporte
    Dado que reporté una publicación y un moderador eligió "Ignorar"
    Cuando abro mis reportes
    Entonces veo ese reporte con el estado "descartado"

  Escenario: El moderador actúa sobre el contenido
    Dado que reporté una publicación y un moderador eligió "Eliminar contenido" o "Suspender autor"
    Cuando abro mis reportes
    Entonces veo ese reporte con el estado "resuelto"
    Y veo la resolución "Se tomó acción sobre el contenido reportado."

  Escenario: Mi reporte sigue abierto
    Dado que reporté una publicación y ningún moderador la ha revisado
    Cuando abro mis reportes
    Entonces veo ese reporte con el estado "enviado"
    Y no veo ninguna resolución