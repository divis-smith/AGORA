# language: es
Característica: Autenticación de usuarios
  Como estudiante
  Quiero registrarme e iniciar sesión
  Para acceder a Ágora

  # Referencia: RF-01 y RF-02. Es un ejemplo de la línea base; lo validamos al planear el Sprint 1.

  Escenario: Registro exitoso
    Dado que soy un visitante sin cuenta
    Cuando completo nombre, correo, carrera, universidad y contraseña
    Y las dos contraseñas coinciden
    Entonces se crea mi cuenta con rol estudiante
    Y veo el mensaje "¡Cuenta creada! Ya puedes entrar."
    Y me lleva a la pantalla de inicio de sesión

  Escenario: Registro con correo ya usado
    Dado que ya existe una cuenta con el correo "vale@correounivalle.edu"
    Cuando intento registrarme con ese correo
    Entonces veo el mensaje "Ese correo ya está registrado."
    Y no se crea una cuenta nueva

  Escenario: Registro con contraseñas distintas
    Dado que soy un visitante sin cuenta
    Cuando escribo una contraseña y una confirmación diferentes
    Entonces veo el mensaje "Las contraseñas no coinciden."
    Y no se crea una cuenta nueva

  Escenario: Inicio de sesión exitoso
    Dado que tengo una cuenta activa
    Cuando ingreso mi correo y mi contraseña correctos
    Entonces accedo al feed con la sesión iniciada
    Y mis permisos corresponden a mi rol

  Escenario: Inicio de sesión con contraseña incorrecta
    Dado que tengo una cuenta activa
    Cuando ingreso mi correo con una contraseña incorrecta
    Entonces veo el mensaje "Correo o contraseña incorrectos."
    Y no se inicia sesión

  Escenario: Inicio de sesión con una cuenta suspendida
    Dado que mi cuenta fue suspendida por un moderador
    Cuando ingreso mi correo y mi contraseña correctos
    Entonces veo el mensaje "Tu cuenta está suspendida. Contacta a un administrador."
    Y no se inicia sesión
