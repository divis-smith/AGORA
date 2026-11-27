# language: es
Característica: SECRET_KEY obligatoria fuera del modo desarrollo
  Como equipo que va a publicar Ágora
  Quiero que la aplicación no arranque en producción sin una SECRET_KEY segura
  Para que nadie pueda falsificar las sesiones con la clave de desarrollo

  # Referencia: Issue #39 (RNF-03).

  Escenario: Arrancar en desarrollo sin configurar nada
    Dado que no definí AGORA_ENTORNO ni SECRET_KEY
    Cuando arranco la aplicación
    Entonces arranca en modo desarrollo con la clave de desarrollo

  Escenario: Arrancar en producción sin SECRET_KEY
    Dado que definí AGORA_ENTORNO=produccion
    Y no definí SECRET_KEY
    Cuando arranco la aplicación
    Entonces no arranca
    Y el mensaje explica cómo generar una clave

  Escenario: Arrancar en producción con una clave de ejemplo o muy corta
    Dado que definí AGORA_ENTORNO=produccion
    Y SECRET_KEY es "dev-only-change-me", "replace-with-a-random-value" o tiene menos de 32 caracteres
    Cuando arranco la aplicación
    Entonces no arranca

  Escenario: Arrancar en producción con una clave aleatoria
    Dado que definí AGORA_ENTORNO=produccion
    Y SECRET_KEY es una clave aleatoria de 64 caracteres
    Cuando arranco la aplicación
    Entonces arranca en modo producción
