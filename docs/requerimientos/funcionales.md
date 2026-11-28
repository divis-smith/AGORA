# Requerimientos funcionales (línea base)

El documento de diagramas de Agora (`docs/legacy/Diagramas_ICONIX.drawio`) trae la descripción del problema y los casos de uso por módulo, pero no una lista numerada de requerimientos. Esta lista la armamos a partir de esos casos de uso, agrupados por módulo y numerados desde el RF-01. Los requerimientos nuevos siguen desde el RF-45 y entran como Issue con la plantilla.

En la columna Estado anotamos si el requerimiento ya está hecho en `main`: "Sí" cuando la operación principal existe en el código, "Parcial" cuando falta algo y "No" cuando no existe. Entre paréntesis va la explicación.

| ID | Módulo | Descripción | Estado |
|---|---|---|---|
| RF-01 | Autenticación | El sistema debe permitir registrar una cuenta nueva con nombre, correo, carrera, universidad y contraseña. La cuenta nace con rol estudiante. | Sí |
| RF-02 | Autenticación | El sistema debe permitir iniciar y cerrar sesión con correo y contraseña, asignando el rol de la cuenta (estudiante, moderador o administrador). Una cuenta suspendida no puede entrar y pierde su sesión abierta. | Sí |
| RF-03 | Autenticación | El sistema debe permitir verificar la cuenta del usuario. | No: la tabla `usuarios` tiene el campo `verificado`, pero ningún flujo lo cambia |
| RF-04 | Autenticación | El sistema debe permitir recuperar la contraseña. | No |
| RF-05 | Feed | El sistema debe mostrar el feed de publicaciones y permitir filtrarlo por categoría (académico, meme, foro, portafolio, general). | Sí: el orden es por fecha; no hay feed personalizado |
| RF-06 | Feed | El sistema debe permitir crear una publicación con título, contenido, categoría, imagen opcional y opción de publicar de forma anónima. | Sí |
| RF-07 | Feed | El sistema debe permitir al autor editar y eliminar sus publicaciones. | Sí |
| RF-08 | Feed | El sistema debe permitir reaccionar a una publicación y quitar la reacción. | Sí |
| RF-09 | Feed | El sistema debe permitir comentar una publicación y consultar sus comentarios. | Sí: comentar y listar; las respuestas anidadas (`padre_id`) y las reacciones a comentarios existen en la base de datos pero no en el código |
| RF-10 | Feed | El sistema debe permitir agregar hashtags a las publicaciones y elegir su visibilidad (todos, seguidores o carrera). | No: las columnas `hashtags` y `visibilidad` existen, pero el formulario y los servicios no las usan |
| RF-11 | Perfil | El sistema debe permitir consultar el perfil propio y el de otros usuarios con sus publicaciones y estadísticas. | Sí |
| RF-12 | Perfil | El sistema debe permitir seguir y dejar de seguir a otros usuarios y consultar la lista de seguidores y de seguidos. | Sí |
| RF-13 | Perfil | El sistema debe permitir crear proyectos en el portafolio (con imagen opcional), consultar el portafolio y aplaudir proyectos. | Sí |
| RF-14 | Perfil | El sistema debe permitir ver el detalle de un proyecto, editarlo, eliminarlo y comentarlo. | Parcial: se puede abrir el detalle de un proyecto desde el portafolio (autor, descripción, tecnologías, estado, enlaces, aplausos y comentarios), aplaudirlo y comentarlo; faltan editar y eliminar |
| RF-15 | Foros | El sistema debe permitir consultar los foros y las preguntas de cada uno. | Sí |
| RF-16 | Foros | El sistema debe permitir crear preguntas en un foro (tipos: pregunta, apuntes, duda, recurso y debate), con opción anónima. | Sí |
| RF-17 | Foros | El sistema debe permitir responder preguntas, votar las respuestas y que el autor marque una como aceptada. | Sí |
| RF-18 | Foros | El sistema debe permitir suscribirse a un foro. | No |
| RF-19 | Explorar | El sistema debe permitir buscar publicaciones, personas y foros por texto. | Sí |
| RF-20 | Explorar | El sistema debe permitir buscar proyectos. | No: la búsqueda solo cubre publicaciones, personas y foros |
| RF-21 | Explorar | El sistema debe mostrar tendencias y el detalle de cada tendencia. | Parcial: lista las publicaciones en tendencia; la sección de hashtags populares queda vacía y no hay vista de detalle |
| RF-22 | Ajustes | El sistema debe permitir modificar el perfil (nombre, biografía, carrera, universidad y foto). | Sí |
| RF-23 | Ajustes | El sistema debe permitir cambiar el correo y la contraseña, pidiendo la contraseña actual. | Sí |
| RF-24 | Ajustes | El sistema debe permitir configurar la privacidad, las notificaciones, la apariencia y el idioma. | No: la pantalla de ajustes no tiene estas secciones ni hay tablas para guardarlas |
| RF-25 | Ayuda | El sistema debe ofrecer una sección de ayuda y soporte con preguntas frecuentes y un canal de contacto. | Parcial: la página `/ayuda` tiene preguntas frecuentes y un correo de contacto; no hay formulario de soporte |
| RF-26 | Eventos | El sistema debe permitir consultar los eventos próximos por categoría y ver el detalle de cada uno. | Sí |
| RF-27 | Eventos | El sistema debe permitir crear un evento con fecha, hora, lugar, cupos y organizador. | Sí |
| RF-28 | Eventos | El sistema debe permitir al creador editar su evento. | Sí |
| RF-29 | Eventos | El sistema debe permitir eliminar un evento al creador, al moderador o al administrador. | Sí |
| RF-30 | Eventos | El sistema debe permitir inscribirse a un evento y cancelar la inscripción, respetando el cupo. | Sí |
| RF-31 | Eventos | El sistema debe permitir ver los participantes de un evento. | Sí |
| RF-32 | Reportes | El sistema debe permitir reportar una publicación, un comentario o un usuario, evitando reportes duplicados abiertos. | Parcial: se puede reportar una publicación desde su detalle (botón «⚑ Reportar» y modal) y nadie puede reportar su propio contenido; faltan los botones para comentarios y usuarios, y las plantillas `reportar_*.html` siguen sin ruta |
| RF-33 | Reportes | El sistema debe permitir al usuario consultar el estado de sus reportes. | Sí: la ruta `/reportes` muestra los reportes del usuario con su sesión y su estado actual; si no tiene reportes, muestra un mensaje informativo |
| RF-34 | Moderación | El sistema debe permitir al moderador y al administrador revisar los reportes abiertos. | Sí |
| RF-35 | Moderación | El sistema debe permitir resolver un reporte: ignorarlo, eliminar el contenido o suspender al usuario. | Sí |
| RF-36 | Moderación | El sistema debe permitir aprobar publicaciones pendientes y levantar las sanciones. | Parcial: una cuenta suspendida se reactiva desde `/admin/usuarios` (#20). El estado `pendiente` existe en la base de datos pero no se usa |
| RF-37 | Administración | El sistema debe ofrecer al administrador un panel con estadísticas (usuarios activos, publicaciones totales, reportes abiertos y eventos próximos). | Sí: `/admin` muestra los cuatro totales y enlaza a moderación; solo entra el administrador (enlace "Administración" en el menú lateral). Gestión de usuarios enlaza a `/admin/usuarios`, gestión de foros a `/admin/foros` y estadísticas a `/admin/estadisticas`, que muestra los posts por categoría, el top 5 de publicadores (sin contar publicaciones anónimas) y los registros por día de los últimos 7 días (#33) |
| RF-38 | Administración | El sistema debe permitir al administrador gestionar usuarios (banear, desbanear, editar y cambiar el rol). | Parcial: en `/admin/usuarios` el administrador busca usuarios por nombre o correo y cambia su rol, y suspende o reactiva cuentas (no puede cambiar su propio rol ni suspenderse a sí mismo). Falta editar sus datos |
| RF-39 | Administración | El sistema debe permitir al administrador gestionar los foros (crear, editar y eliminar). | Parcial: en `/admin/foros` el administrador crea foros (nombre único sin importar mayúsculas, categoría de una lista fija) y los elimina con sus preguntas, respuestas y votos (#32). Falta editarlos |
| RF-40 | Notificaciones | El sistema debe generar notificaciones por eventos relevantes (seguidores nuevos, reacciones, comentarios, respuestas en foros, eventos, mensajes y reportes). | Parcial: se guarda una notificación cuando alguien te sigue o comenta tu publicación (no cuando es tu propio comentario). Faltan reacciones, respuestas en foros, eventos, mensajes y reportes |
| RF-41 | Notificaciones | El sistema debe permitir consultar las notificaciones y marcarlas como leídas. | Sí: en `/notificaciones` se marca una sola (botón ✓ o al abrirla) o todas a la vez; abrir la página ya no las marca |
| RF-42 | Notificaciones | El sistema debe permitir eliminar notificaciones. | Sí: botón ✕ en cada notificación de `/notificaciones` |
| RF-43 | Mensajería | El sistema debe permitir consultar las conversaciones, con el contador de no leídos, y archivarlas. | Sí |
| RF-44 | Mensajería | El sistema debe permitir enviar y recibir mensajes privados en tiempo real. | Sí: usa Socket.IO |

Las pantallas de administración de publicaciones y de eventos que aparecen en el documento (10.2 y 10.4) hoy se cubren con la moderación de reportes (RF-35) y con la eliminación de eventos por moderador (RF-29); no existen como pantallas propias.

El estado lo sacamos leyendo el código, corriendo los 72 tests y visitando cada ruta con cuentas de prueba (estudiante, moderador y administrador). Cuando escribamos el Gherkin de cada requerimiento lo confirmamos corriendo la aplicación y ajustamos esta tabla.
