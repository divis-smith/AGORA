# Cómo trabajamos

Desarrollamos el proyecto con Scrum y llevamos el tablero Kanban en GitHub Projects. Lo de DevOps lo vamos agregando a medida que lo veamos en clase. La integración continua ya existe: `.github/workflows/tests.yml` corre los tests en cada push y en cada Pull Request hacia `main`.

## Dónde queda cada cosa

| Qué | Dónde |
|---|---|
| Product Backlog | GitHub Project, vista Table y columna Backlog |
| Sprint Backlog | Columna Sprint Backlog y el campo Sprint |
| Épicas, historias de usuario e historias técnicas | Issues (plantillas en `.github/ISSUE_TEMPLATE/`) |
| Requerimientos funcionales y no funcionales | `docs/requerimientos/` y Issues con la etiqueta `RF` o `RNF` |
| Criterios de aceptación | Gherkin dentro del Issue y en `features/` |
| DoD y DoR | `docs/DoD.md` y `docs/DoR.md` |
| Actas | `docs/sprints/` |
| Diagramas | Código Mermaid en `docs/diagramas/` |
| Cambios de diseño | Pull Request con el checklist de la plantilla |

## Roles

- **Product Owner:** es el dueño del backlog. Define y prioriza los requerimientos y acepta o rechaza el trabajo.
- **Scrum Master:** se encarga de que el proceso se cumpla, convoca las ceremonias y ayuda a quitar los impedimentos.
- **Equipo de desarrollo:** estima, construye y entrega el incremento.

### Cómo repartimos los roles entre los dos grupos

Cada grupo es dueño de su proyecto y desarrolla el del otro, así que cada uno tiene dos roles:

- En el proyecto propio hay un Product Owner. Los demás son Code Owners: revisan y aprueban los Pull Requests y ayudan al PO a aclarar el backlog.
- En el proyecto del otro grupo hay un Scrum Master y los demás son desarrolladores.

Un solo PO por proyecto, el PO y el Scrum Master no pueden ser la misma persona, el Scrum Master también programa y el Scrum Master rota cada sprint.

### Grupo Agora (dueño de este repositorio, Sprint 1)

Los tres Code Owners están en `.github/CODEOWNERS`. Divis es el Product Owner de Agora y no figura en esa lista: el PO define y prioriza el backlog, y los Code Owners revisan y aprueban los Pull Requests.

| Integrante | Usuario de GitHub | En Agora | En Galezarzal |
|---|---|---|---|
| Valentina Montaño | `montanovalentina-cyber` | Code Owner | Desarrollador (Scrum Master en el Sprint 2) |
| Divis Smith Ramírez | `divis-smith` | Product Owner | Desarrollador |
| Cristian Felipe Arango Gómez | `cristianfelipearango-cmyk` | Code Owner | Scrum Master (Sprint 1) |
| Juan Cardona | `Juacoelseco` | Code Owner | Desarrollador (Scrum Master en el Sprint 3) |

El Scrum Master de Galezarzal rota así: Sprint 1 Cristian, Sprint 2 Valentina, Sprint 3 Juan Cardona.

### Grupo Galezarzal (desarrolla en este repositorio, Sprint 1)

| Integrante | Usuario de GitHub | En Agora | En Galezarzal |
|---|---|---|---|
| Michael Calderon | `mihzuk` | Desarrollador | Product Owner |
| Johan Vallecilla | `Johan-v-p` | Desarrollador (Scrum Master en el Sprint 2) | Code Owner |
| José David Vergara | `Josdaver3000` | Scrum Master (Sprint 1) | Code Owner |
| Carlos Lizarazo | `lizarazo2005` | Desarrollador (Scrum Master en el Sprint 3) | Code Owner |

El Scrum Master de Agora rota así: Sprint 1 José David, Sprint 2 Johan, Sprint 3 Carlos.

Falta confirmar con el profe si el PO y el Scrum Master de cada proyecto salen del grupo dueño o del que desarrolla, y quién asiste a cada ceremonia. Si responde otra cosa, ajustamos este reparto.

## Ceremonias

| Ceremonia | Cuándo | Qué se define | Evidencia |
|---|---|---|---|
| Sprint Planning | Al empezar el sprint | El Sprint Goal y todo el Sprint Backlog | Acta (`_plantilla-sprint-planning.md`) y los Issues movidos a Sprint Backlog |
| Daily | Cada día de trabajo, 15 minutos | Qué hice, qué voy a hacer y qué me bloquea | Acta corta por semana o comentarios en los Issues |
| Refinamiento | Durante el sprint | Detallar y estimar las historias que vienen | Issues actualizados que cumplan el DoR |
| Sprint Review | Al terminar el sprint | Comparar lo comprometido con lo entregado y mostrar el incremento | Acta (`_plantilla-sprint-review.md`) y un tag o release |
| Retrospectiva | Después de la Review | Qué mejorar en la forma de trabajar | Acta con los compromisos |

El profe pidió que cada Sprint Planning tenga un acta clara con el Sprint Goal y todo el Sprint Backlog, porque la revisa en cada Sprint Review. Por eso el acta de la Review siempre se compara con la de Planning. Si algo cambia a mitad del sprint, se anota en la tabla de cambios del acta de Planning sin borrar lo que había.

También quedó claro que cualquier entrega de información o de requerimientos se hace de forma formal, con un acta o con el Issue que corresponda. Lo que se hable solo por chat no cuenta hasta que quede en GitHub.

## Tablero

Las columnas son Backlog, Sprint Backlog, In Progress, In Review y Done. Los campos que usamos son Sprint, Story Points, Prioridad y Tipo (épica, historia de usuario, historia técnica, bug o acta).

- Una tarjeta pasa a In Progress cuando alguien crea su rama.
- Pasa a In Review cuando se abre el Pull Request.
- Pasa a Done cuando el PR se fusiona (con `Closes #N` se mueve sola).
- Cada persona trabaja máximo en dos tarjetas a la vez.

## Cómo trabajamos con Git

1. Cada Issue se trabaja en su rama: `feat/12-hashtags`, `fix/15-panel-admin`, `docs/20-actas`. Son los mismos prefijos que escucha el CI (`feat/`, `fix/`, `chore/`, `refactor/`); para documentación usamos `docs/`.
2. Commits pequeños y con mensajes que se entiendan, por ejemplo `feat(foros): suscribirse a un foro (#14)`.
3. Pull Request con la plantilla y enlazado al Issue. Los tests del CI tienen que pasar.
4. Lo revisa y lo aprueba un Code Owner. En `main` no se hacen commits directos.

## Cambios de diseño

Todo cambio que altere el diseño original obliga a actualizar los diagramas y la documentación. Lo hacemos así:

1. Si un Issue o un PR cambia el diseño, se marca la casilla "Altera el diseño original" en el PR y se enlaza un Issue de tipo Cambio de diseño.
2. El PR no se aprueba hasta que los diagramas, los requerimientos, el Gherkin y `scripts/esquema.sql` afectados estén actualizados en ese mismo PR.
3. El historial de Git queda como prueba de cada cambio y de por qué se hizo.

## Convenciones

- Los Issues y la documentación van en español.
- Los identificadores son `RF-XX` y `RNF-XX`. Del RF-01 al RF-44 y del RNF-01 al RNF-07 ya existen (los armamos a partir de los casos de uso del documento de diagramas y del código; ver `docs/requerimientos/`); los nuevos siguen la numeración.
- La línea base es el estado del proyecto cuando empezamos con Scrum, marcada con el tag `v1.0-baseline`.
