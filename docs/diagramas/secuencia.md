# Diagramas de secuencia

## Iniciar sesión (RF-02): `POST /login`

```mermaid
sequenceDiagram
    actor U as Estudiante
    participant R as rutas/autenticacion.py
    participant S as servicios/cuentas.py
    participant DB as SQLite (usuarios)

    U->>R: POST correo + contraseña
    alt falta el correo o la contraseña
        R-->>U: "Completa todos los campos."
    else datos completos
        R->>S: obtener_por_correo(correo)
        S->>DB: SELECT * FROM usuarios WHERE correo = ?
        DB-->>S: fila (o vacío)
        R->>S: verificar_password(usuario, password)
        alt credenciales correctas y cuenta activa
            R->>R: session guarda user_id, nombre, carrera, universidad y rol
            R-->>U: redirige a /feed
        else cuenta suspendida
            R-->>U: "Tu cuenta está suspendida. Contacta a un administrador."
        else credenciales incorrectas
            R-->>U: "Correo o contraseña incorrectos."
        end
    end
```

## Reportar y resolver un reporte (RF-32 y RF-35): `POST /reporte/nuevo` y `POST /moderacion/resolver/<id>`

Hoy ninguna pantalla llama a `/reporte/nuevo` (RF-32), pero el servicio funciona y tiene tests.

```mermaid
sequenceDiagram
    actor E as Estudiante
    actor M as Moderador
    participant R as rutas/moderacion.py
    participant S as servicios/moderacion.py
    participant DB as SQLite

    E->>R: POST tipo, contenido_id y motivo
    R->>R: valida tipo (publicación, comentario o usuario) y datos
    R->>S: obtener_usuario_reportado(tipo, contenido_id)
    alt el contenido no existe
        R-->>E: 404 "El contenido reportado no existe."
    else ya hay un reporte abierto del mismo usuario
        R-->>E: "Ya reportaste este contenido."
    else reporte nuevo
        R->>S: crear_reporte(...)
        S->>DB: INSERT INTO reportes (estado enviado)
        R-->>E: ok
    end

    M->>R: POST accion (ignorar, eliminar o suspender)
    R->>R: login_required + moderador_required
    R->>S: obtener_reporte(id)
    alt la acción es eliminar
        R->>S: eliminar_contenido_reportado(reporte)
    else la acción es suspender
        R->>S: suspender_usuario(objetivo)
        S->>DB: UPDATE usuarios SET activo = 0
    end
    R->>S: cerrar_reporte(id, moderador)
    S->>DB: UPDATE reportes SET estado = resuelto
    R-->>M: "Reporte #N resuelto"
```

## Inscribirse a un evento (RF-30): `POST /eventos/<id>/inscribir`

```mermaid
sequenceDiagram
    actor E as Estudiante
    participant R as rutas/eventos.py
    participant S as servicios/eventos.py
    participant DB as SQLite

    E->>R: POST /eventos/id/inscribir
    R->>S: obtener_cupos(id)
    alt el evento no existe
        R-->>E: 404 "Evento no encontrado"
    else existe
        R->>S: alternar_inscripcion(id, usuario, cupos)
        S->>DB: ¿ya está inscrito?
        alt ya estaba inscrito
            S->>DB: DELETE inscripción
            S-->>R: False (se canceló)
        else no estaba inscrito
            alt hay cupos o el evento no tiene límite
                S->>DB: INSERT inscripción
                S-->>R: True (quedó inscrito)
            else el cupo está lleno
                S-->>R: None
                R-->>E: 400 "Sin cupos disponibles"
            end
        end
        R-->>E: ok, inscrito y cupos libres
    end
```

## Enviar un mensaje privado (RF-44): `POST /mensajes/<conv_id>/enviar`

```mermaid
sequenceDiagram
    actor E as Estudiante
    participant R as rutas/mensajes.py
    participant S as servicios/mensajes.py
    participant DB as SQLite
    participant WS as Socket.IO

    E->>R: POST contenido
    alt vacío o de más de 1000 caracteres
        R-->>E: 400
    else contenido válido
        R->>S: participa(conv_id, usuario)
        alt no participa en la conversación
            R-->>E: 403
        else participa
            R->>S: guardar_mensaje(conv_id, usuario, contenido)
            S->>DB: INSERT INTO mensajes
            R->>WS: emit mensaje_nuevo a la sala del remitente
            R->>WS: emit mensaje_nuevo a la sala del receptor
            R->>WS: emit notificacion al receptor ("te envió un mensaje")
            R-->>E: ok, msg_id y hora
        end
    end
```
