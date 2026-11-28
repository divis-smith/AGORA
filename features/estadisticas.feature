# language: es
Característica: Estadísticas de la plataforma
  Como administrador
  Quiero ver estadísticas de actividad de la plataforma
  Para saber qué se publica y cuánta gente se registra

  # Referencia: Issue #33, RF-37 y RNF-08.
  # Pruebas automáticas: tests/test_estadisticas.py

  Escenario: Ver las estadísticas
    Dado que soy administrador y estoy en el panel de administración
    Cuando pulso "Estadísticas"
    Entonces veo "Posts por categoría", "Top publicadores" y "Nuevos usuarios — últimos 7 días"
    Y la página no responde error

  Escenario: Las publicaciones anónimas no cuentan para el top
    Dado que un estudiante tiene publicaciones anónimas y ninguna pública
    Cuando abro "Estadísticas"
    Entonces ese estudiante no aparece en "Top publicadores"

  Escenario: Todavía no hay datos
    Dado que no hay publicaciones ni registros en los últimos 7 días
    Cuando abro "Estadísticas"
    Entonces veo "Sin datos aún." y "No hubo registros en los últimos 7 días."

  Escenario: Un estudiante intenta entrar
    Dado que inicié sesión como estudiante
    Cuando intento abrir /admin/estadisticas
    Entonces veo el mensaje "Acceso denegado."
    Y soy llevado al feed
