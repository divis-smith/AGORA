# Colaboración entre grupos

Cada grupo le entrega los requerimientos al otro. El grupo que creó un proyecto escribe los requerimientos nuevos y el otro grupo los desarrolla. Falta validar con el profe el detalle de los roles de Scrum entre grupos; cuando responda ajustamos este documento.

## Cómo trabajamos

Cada grupo tiene dos papeles al mismo tiempo: es dueño de su repositorio y desarrolla el del otro. En este repositorio, el de Agora:

- El grupo Agora actúa como Product Owner. Escribe los requerimientos nuevos para el otro grupo (épicas e historias con su Gherkin), mantiene el backlog, prioriza y aprueba los Pull Requests.
- El grupo Galezarzal trabaja como equipo de desarrollo. Toma los Issues del sprint, trabaja en ramas o en un fork y abre los Pull Requests.
- El profe revisa épicas, historias, requerimientos, Gherkin, DoD, diagramas y actas.

Los roles de cada persona están en [`scrum.md`](scrum.md#roles).

## Cómo se entrega un requerimiento

1. El grupo dueño abre el Issue con la plantilla que corresponda: épica, historia o solicitud de requerimiento. El grupo que desarrolla también puede abrir una solicitud para proponer o aclarar algo, pero la decisión es del dueño.
2. El Product Owner lo afina hasta que cumpla el DoR (`DoR.md`).
3. Entra al Product Backlog y se prioriza.
4. Se planea en un sprint, con su acta de Planning.

Si algo solo se dijo por chat, no cuenta como entregado.

## Cómo se entrega el trabajo

1. Una rama o un fork por Issue y un Pull Request con la plantilla.
2. Si el cambio altera el diseño, en el mismo PR se actualizan los diagramas, la documentación, el Gherkin y `scripts/esquema.sql`.
3. Un Code Owner del grupo dueño aprueba y fusiona.
4. El Issue se cierra y la tarjeta pasa a Done.

## Acuerdos

- Todo lo que afecte al proyecto queda en Issues, PRs o actas.
- Si hay desacuerdo sobre el alcance, se resuelve en el Issue; si no se logra, se lo preguntamos al profe.
- En la Sprint Review cada grupo muestra lo que hizo sobre el repositorio del otro.
