# Backlog inicial

Candidatos para arrancar el Product Backlog. Salen de leer el código de `main`, de correr los 72 tests y de visitar cada ruta con una cuenta de estudiante, una de moderador y una de administrador. Son propuestas para que el Product Owner de Agora las revise: las que entren y su prioridad las decide el PO. Estado revisado sobre `main` el 10 de noviembre de 2026.

El detalle de qué está hecho y qué no está en [`requerimientos/funcionales.md`](requerimientos/funcionales.md).

## Bugs

Hoy dos pantallas responden error 500. Arreglarlas no cambia el diseño, solo conecta lo que ya existe.

| # | Tipo | Problema | RF |
|---|---|---|---|
| 1 | Bug | `/admin` responde 500. La ruta le pasa los contadores a `panel.html` con `**totales`, pero la plantilla espera una variable `stats`, y además enlaza a rutas que no existen (`admin_usuarios`, `admin_foros`, `admin_estadisticas`). | RF-37 |
| 2 | Bug | `/reportes` responde 500. `reportes.html` enlaza a `reportar_publicacion`, `reportar_comentario` y `reportar_usuario`, que no existen en ningún Blueprint. | RF-33 |

## Candidatos nuevos

| # | Tipo | Propuesta | RF o RNF |
|---|---|---|---|
| 3 | HU | Interfaz para reportar: botones en la publicación, el comentario y el perfil que llamen a `POST /reporte/nuevo` (el servicio ya existe y tiene tests). Las plantillas `reportar_*.html` están sin ruta. | RF-32 |
| 4 | HU | Hashtags y visibilidad en las publicaciones. Las columnas existen en la base de datos pero el formulario no las usa; con esto la sección "Hashtags populares" de tendencias deja de estar vacía. | RF-10, RF-21 |
| 5 | HU | Verificar la cuenta y recuperar la contraseña. | RF-03, RF-04 |
| 6 | HU | Notificaciones por reacciones, comentarios, respuestas en foros, eventos y reportes. Hoy solo se guarda una cuando alguien te sigue. Incluye marcar una como leída y eliminarla. | RF-40, RF-41, RF-42 |
| 7 | HU | Preferencias de privacidad, notificaciones, apariencia e idioma en Ajustes. No hay pantalla ni tablas para guardarlas. | RF-24 |
| 8 | HU | Gestión de usuarios para el administrador: banear, desbanear, editar y cambiar el rol. Hoy un usuario suspendido no se puede reactivar desde la aplicación. | RF-36, RF-38 |
| 9 | HU | Gestión de foros para el administrador (crear, editar, eliminar) y suscribirse a un foro. Hoy los foros solo salen de los datos de demostración. | RF-18, RF-39 |
| 10 | HU | Detalle de proyecto del portafolio: ver, editar, eliminar y comentar (`ver_proyecto.html` y la tabla `comentarios_proyecto` ya existen). | RF-14 |
| 11 | HU | Buscar proyectos y ver el detalle de una tendencia. | RF-20, RF-21 |
| 12 | HU | Formulario de soporte en la sección de ayuda (hoy solo hay un correo). | RF-25 |
| 13 | HT | Protección CSRF en los formularios y cambiar el `SECRET_KEY` por defecto (`dev-only-change-me`) para que sea obligatorio fuera de desarrollo. Revisar también `cors_allowed_origins='*'` de Socket.IO. | RNF-03 |
| 14 | HT | Una prueba que visite todas las páginas con cada rol y falle si alguna responde 500. Habría detectado los bugs 1 y 2. Hoy los tests no cubren registro, foros, eventos, mensajes ni búsqueda. | RNF-07 |
| 15 | HT | Limpiar las plantillas sin ruta (`estadisticas`, `foros`, `usuarios`, `mis_reportes`, `reportar*` y `ver_proyecto`): conectarlas a una historia o borrarlas. | RNF-07 |
| 16 | HT | Escribir el Gherkin de lo que ya existe y confirmar cada RF corriendo la aplicación. | RF-01 a RF-44 |
| 17 | HT | Definir cómo probamos cada escenario Gherkin (a mano y documentado al principio, automático después). | DoD |
| 18 | HT | Documentar el despliegue y, cuando lo veamos en clase, montar CD. La integración continua (tests en cada PR) ya existe. | RNF-02 |
| 19 | HT | Medir el tiempo de respuesta del feed y de la búsqueda, y revisar la compatibilidad en móvil y en navegadores. | RNF-01, RNF-04, RNF-06 |
