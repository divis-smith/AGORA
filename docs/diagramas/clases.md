# Diagrama de clases del dominio

Parte de las entidades del diagrama de dominio del documento original (`docs/legacy/Diagramas_ICONIX.drawio`) y del modelo de datos. Los atributos son los de `scripts/esquema.sql`. El código de Agora no define clases de dominio: usa funciones de servicio sobre SQLite, así que este diagrama es conceptual.

```mermaid
classDiagram
    class Usuario {
        +int id
        +string nombre
        +string correo
        +string carrera
        +string universidad
        +int semestre
        +string bio
        +string avatar_url
        +string rol
        +bool verificado
        +bool activo
    }
    class Publicacion {
        +int id
        +string titulo
        +string contenido
        +string categoria
        +string hashtags
        +string imagen_url
        +string visibilidad
        +string estado
        +bool es_anonimo
        +datetime creado_en
    }
    class Comentario {
        +int id
        +string contenido
        +datetime creado_en
    }
    class Foro {
        +int id
        +string nombre
        +string descripcion
        +string categoria
    }
    class PreguntaForo {
        +int id
        +string tipo
        +string titulo
        +string contenido
        +bool es_anonimo
    }
    class RespuestaForo {
        +int id
        +string contenido
        +bool es_anonimo
        +bool aceptada
    }
    class Proyecto {
        +int id
        +string titulo
        +string descripcion
        +string tecnologias
        +string materia
        +string estado
        +string repo_url
        +string demo_url
        +bool destacado
    }
    class Evento {
        +int id
        +string titulo
        +string descripcion
        +string categoria
        +date fecha
        +time hora_inicio
        +time hora_fin
        +string lugar
        +int cupos
        +string organizador
    }
    class Conversacion {
        +int id
        +datetime ultimo_msg
    }
    class Mensaje {
        +int id
        +string contenido
        +bool leido
        +datetime creado_en
    }
    class Notificacion {
        +int id
        +string tipo
        +string mensaje
        +bool leida
        +string url
    }
    class Reporte {
        +int id
        +string tipo
        +int referencia_id
        +string motivo
        +string estado
        +string resolucion
    }

    Usuario "1" --> "*" Publicacion : publica
    Publicacion "1" --> "*" Comentario : tiene
    Usuario "1" --> "*" Comentario : escribe
    Comentario "0..1" --> "*" Comentario : responde a
    Usuario "*" --> "*" Publicacion : reacciona
    Usuario "*" --> "*" Usuario : sigue
    Usuario "1" --> "*" Foro : crea
    Foro "1" --> "*" PreguntaForo : contiene
    PreguntaForo "1" --> "*" RespuestaForo : recibe
    Usuario "*" --> "*" RespuestaForo : vota
    Usuario "1" --> "*" Proyecto : tiene en su portafolio
    Usuario "*" --> "*" Proyecto : aplaude
    Usuario "1" --> "*" Evento : crea
    Usuario "*" --> "*" Evento : se inscribe
    Conversacion "1" --> "*" Mensaje : contiene
    Usuario "*" --> "*" Conversacion : participa
    Usuario "1" --> "*" Mensaje : envía
    Usuario "1" --> "*" Notificacion : recibe
    Usuario "1" --> "*" Reporte : reporta
    Reporte "*" --> "1" Usuario : revisa un moderador
```

## Cosas que tener en cuenta
- `Hashtag` y `Perfil` aparecen en el diagrama de dominio original, pero no existen como entidades en el código: los hashtags son una columna de `publicaciones` que todavía no se usa y el perfil son los campos de `usuarios`.
- Un `Reporte` apunta a una publicación, un comentario o un usuario según su `tipo` (`referencia_id`), por eso no se dibuja como una asociación fija.
- Los comentarios de proyectos (`comentarios_proyecto`) y las publicaciones guardadas (`guardados`) existen en la base de datos, pero el código no los usa todavía.
