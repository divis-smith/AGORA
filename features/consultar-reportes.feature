# language: es
Característica: Estado de mis reportes
  Como estudiante
  Quiero ver el estado de los reportes que hice
  Para saber si los moderadores ya los atendieron

  # Referencia: Issue #7 y RF-33.

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