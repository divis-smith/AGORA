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
| RF-14 | Perfil | El sistema debe permitir ver el detalle de un proyecto, editarlo, eliminarlo y comentarlo. | No: existe la plantilla `portafolio/ver_proyecto.html` y la tabla `comentarios_proyecto`, pero no hay ruta |
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
| RF-32 | Reportes | El sistema debe permitir reportar una publicación, un comentario o un usuario, evitando reportes duplicados abiertos. | Parcial: el servicio (`POST /reporte/nuevo`) funciona y tiene tests, pero ninguna pantalla lo llama; las plantillas `reportar_*.html` no tienen ruta |
| RF-33 | Reportes | El sistema debe permitir al usuario consultar el estado de sus reportes. | Parcial: la ruta `/reportes` existe pero responde error 500 porque `reportes.html` enlaza a rutas que no existen |
| RF-34 | Moderación | El sistema debe permitir al moderador y al administrador revisar los reportes abiertos. | Sí |
| RF-35 | Moderación | El sistema debe permitir resolver un reporte: ignorarlo, eliminar el contenido o suspender al usuario. | Sí |
| RF-36 | Moderación | El sistema debe permitir aprobar publicaciones pendientes y levantar las sanciones. | No: el estado `pendiente` existe en la base de datos pero no se usa, y una cuenta suspendida no se puede reactivar desde la aplicación |
| RF-37 | Administración | El sistema debe ofrecer al administrador un panel con estadísticas (usuarios activos, publicaciones totales, reportes abiertos y eventos próximos). | Parcial: `totales_panel()` calcula los números, pero `/admin` responde error 500 (la plantilla espera otra variable y enlaza a rutas que no existen) |
| RF-38 | Administración | El sistema debe permitir al administrador gestionar usuarios (banear, desbanear, editar y cambiar el rol). | No: existe la plantilla `moderacion/usuarios.html`, pero no hay ruta |
| RF-39 | Administración | El sistema debe permitir al administrador gestionar los foros (crear, editar y eliminar). | No: los foros solo se crean con los datos de demostración |
| RF-40 | Notificaciones | El sistema debe generar notificaciones por eventos relevantes (seguidores nuevos, reacciones, comentarios, respuestas en foros, eventos, mensajes y reportes). | Parcial: solo se guarda una notificación cuando alguien te sigue |
| RF-41 | Notificaciones | El sistema debe permitir consultar las notificaciones y marcarlas como leídas. | Sí: al abrir `/notificaciones` se marcan todas como leídas; no hay marcar una sola |
| RF-42 | Notificaciones | El sistema debe permitir eliminar notificaciones. | No |
| RF-43 | Mensajería | El sistema debe permitir consultar las conversaciones, con el contador de no leídos, y archivarlas. | Sí |
| RF-44 | Mensajería | El sistema debe permitir enviar y recibir mensajes privados en tiempo real. | Sí: usa Socket.IO |

Las pantallas de administración de publicaciones y de eventos que aparecen en el documento (10.2 y 10.4) hoy se cubren con la moderación de reportes (RF-35) y con la eliminación de eventos por moderador (RF-29); no existen como pantallas propias.

El estado lo sacamos leyendo el código, corriendo los 72 tests y visitando cada ruta con cuentas de prueba (estudiante, moderador y administrador). Cuando escribamos el Gherkin de cada requerimiento lo confirmamos corriendo la aplicación y ajustamos esta tabla.
