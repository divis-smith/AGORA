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

Desde el detalle de una publicación, el botón «⚑ Reportar» abre un modal y llama a `/reporte/nuevo` (RF-32). Los comentarios y los perfiles todavía no tienen botón, pero el servicio ya los acepta.

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
    else el contenido es del propio usuario
        R-->>E: 400 "No puedes reportar tu propio contenido."
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
    R->>S: cerrar_reporte(id, moderador, acción)
    alt acción = ignorar
        S->>DB: UPDATE reportes SET estado = descartado, resolucion = NULL, revisado_por y resuelto_en
        R-->>M: "Reporte #N descartado"
    else acción = eliminar o suspender
        S->>DB: UPDATE reportes SET estado = resuelto, resolucion = "Se tomó acción sobre el contenido reportado.", revisado_por y resuelto_en
        R-->>M: "Reporte #N resuelto"
    end
```

## Marcar como leída y eliminar una notificación (RF-41 y RF-42): `POST /notificaciones/<id>/leida` y `POST /notificaciones/<id>/eliminar`

Abrir `/notificaciones` ya no marca todo como leído. En cada notificación, el botón ✓ (o pulsar la notificación) la marca como leída y el botón ✕ la elimina. «Marcar todas como leídas» llama a `POST /notificaciones/leer-todas`. En los tres casos la respuesta trae el nuevo total de no leídas para el contador del menú.

```mermaid
sequenceDiagram
    actor E as Estudiante
    participant R as rutas/social.py
    participant S as servicios/social.py
    participant DB as SQLite (notificaciones)

    E->>R: POST /notificaciones/<id>/leida (o /eliminar)
    R->>S: marcar_notificacion_leida(usuario_id, id) o eliminar_notificacion(usuario_id, id)
    S->>DB: UPDATE (o DELETE) ... WHERE id = ? AND usuario_id = ?
    alt no existe o es de otro usuario (0 filas)
        R-->>E: 404 "La notificación no existe."
    else es del usuario
        R->>S: contar_notificaciones_no_leidas(usuario_id)
        S->>DB: SELECT COUNT(*) ... WHERE usuario_id = ? AND leida = 0
        R-->>E: ok y no_leidas
        E->>E: actualiza la tarjeta y el contador del menú
    end
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
