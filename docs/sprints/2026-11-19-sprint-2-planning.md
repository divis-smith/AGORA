# Acta de Sprint Planning, Sprint 2

| | |
| --- | --- |
| Sprint | 2 |
| Fecha y hora de la reunión | 2026-11-19, de 10:40 PM a 11:20 PM |
| Duración del sprint | 2 semanas |
| Lugar o medio | Meet |
| Scrum Master | José David Vergara Zapata |
| Product Owner | Divis Smith Ramirez |
| Equipo de desarrollo | Johan Andrés Vallecilla, Carlos Enrique Lizarazo, Michael Stivens Calderón Ulloa y José David Vergara Zapata |
| Ausentes y motivo | Ninguno |

## Sprint Goal

Al terminar el sprint, los admins podrán acceder a su panel, podrán gestionar los usuarios y los foros de la plataforma.

Por otro lado, los estudiantes podrán reportar comentarios y perfiles, comentar proyectos, y contar con un perfil público que no revele publicaciones anónimas.

## Sprint Backlog

| Issue | Tipo | Título | RF o RNF | Story points | Responsable | Gherkin listo |
| --- | --- | --- | --- | --- | --- | --- |
| #38 | HT | Protección CSRF en los formularios y peticiones | RNF-03 | 8 | Carlos Enrique Lizarazo | Sí |
| #39 | HT | SECRET_KEY obligatoria fuera del modo desarrollo | RNF-03 | 6 | Carlos Enrique Lizarazo | Sí |
| #24 | HT | El perfil público no debe mostrar publicaciones anónimas | RNF-08; relacionados RF-06 y RF-11 | 7 | Carlos Enrique Lizarazo | Sí |
| #28 | HT | Abrir el chat con mi propia cuenta responde error 500 | RNF-07; relacionado RF-44 | 4 | Carlos Enrique Lizarazo | Sí |
| #41 | HT | El filtro de categorías de foros no filtra | RNF-07; relacionado RF-15 | 6 | Johan Andrés Vallecilla | Sí |
| #40 | HT | La agenda de un evento se muestra como JSON | RNF-07; relacionado RF-26 | 5 | Johan Andrés Vallecilla | Sí |
| #37 | HU | Rechazar contraseñas cortas al registrarse | RF-01 | 5 | Johan Andrés Vallecilla | Sí |
| #35 | HU | Comentar un proyecto | RF-14 | 4 | Johan Andrés Vallecilla | Sí |
| #36 | HU | Buscar proyectos desde Explorar | RF-20 | 6 | Johan Andrés Vallecilla | Sí |
| #34 | HU | Ver el detalle de un proyecto | RF-14 | 4 | Johan Andrés Vallecilla | Sí |
| #20 | HU | Suspender y reactivar cuentas desde el panel | RF-36, RF-38 | 5 | Michael Stivens Calderón Ulloa | Sí |
| #32 | HU | Crear y eliminar foros desde el panel | RF-39 | 5 | Michael Stivens Calderón Ulloa | Sí |
| #33 | HU | Ver estadísticas de la plataforma | RF-37 | 7 | Michael Stivens Calderón Ulloa | Sí |
| #29 | HT | Los datos de demostración deben tener fechas relativas a hoy | RNF-07; relacionados RF-26 y DoD | 7 | Michael Stivens Calderón Ulloa | Sí |
| #21 | HU | Reportar un comentario | RF-32 | 4 | José David Vergara Zapata | Sí |
| #22 | HU | Reportar a un usuario desde su perfil | RF-32 | 3 | José David Vergara Zapata | Sí |
| #26 | HU | Llegar a mis reportes desde el menú | RF-33 | 3 | José David Vergara Zapata | Sí |
| #27 | HU | Saber cómo se resolvió mi reporte | RF-33, RF-35 | 6 | José David Vergara Zapata | Sí |
| #23 | HU | Notificar cuando responden mi pregunta en un foro | RF-40 | 5 | José David Vergara Zapata | Sí |
| #18 | HU | Entrar al panel de administración | RF-37 | 3 | Michael Stivens Calderón Ulloa | Sí |
| #19 | HU | Buscar usuarios y cambiar su rol | RF-38 | 4 | Michael Stivens Calderón Ulloa | Sí |

Total de story points comprometidos: 107

Capacidad estimada del equipo: 107 puntos (segundo sprint; estimación acordada por el equipo)

Todas las historias cumplen el DoR (`docs/DoR.md`): sí.

## Criterio de terminado

Aplica `docs/DoD.md`. Excepciones acordadas: ninguna.

## Dependencias, riesgos e impedimentos

### Dependencias

- **Panel administrativo (`#18` - Michael):** Es prerequisito directo para habilitar el resto de funcionalidades de administración: gestión de roles (`#19`), suspensión/reactivación de cuentas (`#20`), creación/eliminación de foros (`#32`) y estadísticas (`#33`).
- **Vista de detalle de proyecto (`#34` - Johan):** Marcada como prioridad inicial porque es necesaria antes de implementar los comentarios en proyectos (`#35`).
- **Flujo de reportes y moderación (José y Michael):** Consultar los reportes desde el menú (`#26`) y visualizar cómo se resolvió cada caso (`#27`) depende de la generación de reportes (`#21`, `#22`) y de las acciones de moderación/suspensión aplicadas desde el panel admin (`#20`).
- **Foros, datos de prueba y notificaciones (Michael, Johan y José):** La notificación de respuestas en foros (`#23`) y el filtro por categorías (`#41`) interactúan con la gestión de foros (`#32`). Además, la actualización de fechas relativas en los datos de demostración (`#29`) sirve de insumo para validar correctamente las estadísticas (`#33`) y agendas de eventos (`#40`).
- **Protección CSRF (`#38` - Carlos):** Definida como última prioridad porque es un cambio transversal que afecta todos los formularios y peticiones del sistema (`#19`, `#20`, `#21`, `#22`, `#32`, `#35`, `#37`). Debe integrarse cuando los demás endpoints estén estables para no bloquear el avance paralelo.
- **Configuración de entorno (`#39` - Carlos):** La obligatoriedad de `SECRET_KEY` fuera del modo desarrollo requiere que todo el equipo mantenga configuradas sus variables de entorno locales para evitar fallos en pruebas de preproducción.

### Riesgos

- **Alta carga de story points (107 pts en 21 issues):** El volumen comprometido es exigente; cualquier retraso técnico o demora en la revisión de Pull Requests puede impedir completar el 100 % del Sprint Backlog.
- **Regresiones por integración tardía de CSRF (`#38`):** Al aplicarse al final del sprint, existe el riesgo de que formularios o peticiones construidas previamente fallen con error `403 Forbidden` si no se ejecuta una validación integral entre todos los módulos antes del cierre.
- **Posibles ambigüedades funcionales en criterios visuales:** Tareas como el detalle de resolución de reportes (`#27`), el paso de JSON a lista de horas/actividades en la agenda (`#40`) o las métricas del panel (`#33`) pueden requerir aclaraciones puntuales del PO durante el desarrollo.
- **Detección tardía de bloqueos por horario de Daily:** Con las Dailys programadas a las 10:30 PM, un bloqueo ocurrido temprano en el día puede hacer perder la jornada completa si el desarrollador no lo reporta por el grupo de inmediato.

### Impedimentos

- **Impedimentos activos al iniciar el sprint:** Ninguno. El equipo cuenta con el backlog priorizado, estimado y asignado para arrancar sin bloqueos iniciales.
- **Impedimentos potenciales a monitorear:**
  - Dudas de alcance o diseño en historias específicas (`#27`, `#33`, `#40`), mitigadas mediante el acuerdo de consultar directamente al PO (Divis) apenas surja la duda, sin esperar a la Daily nocturna.
  - Conflictos de fusión (*merge conflicts*) en archivos compartidos (plantillas base, rutas principales y configuración global por `#38` y `#39`) debido al trabajo simultáneo de los cuatro integrantes.

## Acuerdos de la reunión

1. Si hay dudas, solicitar aclaración al PO.
2. Las dailys se realizarán a las 10:30 PM. De no haber daily por algún motivo, se informará al equipo y se hará seguimiento en la daily del día siguiente o cuando haya disponibilidad.

## Cambios al Sprint Backlog durante el sprint

Esto se llena después de la reunión y sin borrar lo anterior: fecha, qué cambió, quién lo aprobó y por qué.

| Fecha | Cambio (agregar, quitar o modificar) | Issue | Aprobado por | Motivo |
| --- | --- | --- | --- | --- |
| | | | | |
