# Acta de Daily, Sprint 1

| | |
| --- | --- |
| Ceremonia | Daily (acta semanal, una fila por día) |
| Fecha y hora | Semana del 2026-11-15 al 2026-11-17, todos los días de trabajo a las 5:30 p. m. (15 minutos) |
| Lugar o medio | Meet |
| Scrum Master | José David Vergara Zapata |
| Product Owner | Divis Smith Ramírez |
| Asistentes | Johan Andrés Vallecilla, Carlos Enrique Lizarazo, Michael Stivens Calderón Ulloa y José David Vergara Zapata |
| Ausentes y motivo | Ninguno |

## Temas que vimos

| Día | Asistentes | Qué hizo cada uno | Qué sigue | Impedimentos |
| --- | --- | --- | --- | --- |
| Dom 2026-11-15 | Todos | Johan: terminó #6 (PR #13 fusionado). Michael: estudiando #9. Carlos: analizando #10. José David: preparando #7. | Michael y José David crean su rama y empiezan; Carlos sigue con el análisis; Johan espera nuevas asignaciones | Ninguno |
| Lun 2026-11-16 | Todos | Johan: analizando el proyecto a fondo. Michael: terminó #9 y abrió el PR en borrador. Carlos: terminó #10. José David: creó su rama y desarrolla #7. | Johan espera nuevas asignaciones; Michael y Carlos esperan la revisión de sus PR; José David sigue con #7 | Carlos: conflicto en la fusión de su PR |
| Mar 2026-11-17 | no hubo daily | se cerraron todos los issues del sprint | iniciar sprint 2 | reunion presencial de sprint review con el profesor |
| Mié 2026-11-18 | | | | |
| Jue 2026-11-19 | | | | |
| Vie 2026-11-20 | | | | |

Si un día no hubo Daily, se deja la fila con "No hubo Daily" y el motivo.

### Detalle de la Daily del 2026-11-15

- **Johan Andrés Vallecilla (#6):** leyó el Issue, el Gherkin y los requerimientos, y construyó el botón «Reportar» y el modal con los motivos. En la primera versión del PR #13, el Code Owner Cristian Arango pidió un cambio: el escenario decía estado «abierto», pero la base de datos guarda «enviado». Lo corrigió, lo dejó explicado en el PR y el PR se fusionó. #6 queda en Done. Está a la espera de nuevas asignaciones.
- **Michael Stivens Calderón Ulloa (#9):** está estudiando el problema, el Gherkin y los requerimientos. Sigue crear la rama `feat/9-...` y empezar el código.
- **Carlos Enrique Lizarazo (#10):** está analizando el problema del Issue y el Gherkin.
- **José David Vergara Zapata (#7):** dejó el proyecto corriendo, revisó el trabajo de #6, analizó el Gherkin y el RF-33. Sigue crear la rama `feat/7-consultar-reportes` y empezar la pantalla de mis reportes y lo que solicita el issue.

### Detalle de la Daily del 2026-11-16

- **Johan Andrés Vallecilla:** está analizando el proyecto a fondo. Sigue a la espera de nuevas asignaciones.
- **Michael Stivens Calderón Ulloa (#9):** analizó el proyecto, creó su rama, revisó el problema, programó y probó como estudiante: las notificaciones sí llegan. Abrió el PR, que está en borrador, comentó la Daily en su Issue y espera la revisión.
- **Carlos Enrique Lizarazo (#10):** terminó el Issue. Las notificaciones funcionan: cada una se puede marcar como leída, se pueden marcar todas como leídas y se pueden borrar. Hizo las pruebas. Sin impedimentos graves, solo un conflicto en la fusión.
- **José David Vergara Zapata (#7):** creó su rama, analizó qué archivos modifica y está desarrollando la pantalla. Sin problemas.

### Detalle de la Daily del 2026-11-17

-no hubo Daily. Se cerraron todos los issues del sprint y se pronostico el inicio del sprint 2. Se hizo la reunión presencial de Sprint Review con el profesor.

## Issues revisados

- #6, Reportar una publicación, Done
- #7, Consultar el estado de mis reportes, Done
- #9, Notificar cuando comentan mi publicación, Done
- #10, Marcar una notificación como leída y eliminarla, Done

## Acuerdos y decisiones

1. Después de cada Daily, cada integrante deja un comentario corto en su propio Issue con qué hizo, qué sigue y qué lo bloquea. Queda con fecha y hora automáticas.
2. El acta de la Daily se hace una vez por semana, con una fila por día.
3. Las ramas nuevas usan el prefijo `feat/`, como indica `scrum.md`.
4. Se aclaró que en los PR no se suben imágenes: las evidencias se explican con un pequeño texto.

## Impedimentos o riesgos

- Johan no tiene Issue asignado desde que se fusionó #6. Queda pendiente definir con el product owner Divis si ayuda a probar los demás Issues o si toma la HT #11 (hoy en Backlog, sin puntos).
- Carlos tuvo un conflicto de fusión en el PR de #10. Queda pendiente confirmar si ya lo resolvió.

## Qué sigue

| Acción | Responsable | Fecha límite |
| --- | --- | --- |
| Marcar el PR #9 como listo para revisión (si sigue en borrador) y atender la revisión | Michael | sin definir |
| Revisar y aprobar el PR de #9 | Code Owner de AGORA | sin definir |
| Resolver el conflicto de fusión y atender la revisión del PR de #10 | Carlos | sin definir |
| Revisar y aprobar el PR de #10 | Code Owner de AGORA | sin definir |
| Terminar el Issue #7 | José David | sin definir |
| Definir con Divis si Johan ayuda a probar los demás Issues o toma la HT #11 | José David y Divis | sin definir |
