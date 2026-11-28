# language: es
Característica: Suspender y reactivar cuentas
  Como administrador
  Quiero suspender y reactivar cuentas desde la lista de usuarios
  Para actuar sobre una cuenta sin esperar un reporte

  # Referencia: Issue #20, RF-36 y RF-38.
  # Pruebas automáticas: tests/test_suspender_cuentas.py

  Escenario: Suspender una cuenta
    Dado que soy administrador y veo una cuenta activa en la lista
    Cuando pulso "Suspender" y confirmo
    Entonces la cuenta aparece como "Suspendido"
    Y esa persona ya no puede iniciar sesión

  Escenario: Reactivar una cuenta
    Dado que una cuenta está suspendida
    Cuando pulso "Activar" y confirmo
    Entonces la cuenta aparece como "Activo"
    Y esa persona puede volver a iniciar sesión

  Escenario: Suspender mi propia cuenta
    Dado que soy administrador
    Cuando intento suspender mi propia cuenta
    Entonces veo el mensaje "No puedes suspender tu propia cuenta."
    Y mi cuenta sigue activa
