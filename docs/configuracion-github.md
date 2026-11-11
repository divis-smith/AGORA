# Configuración de GitHub

Lista de lo que hay que dejar listo en el repositorio. Marcamos cada punto cuando esté hecho. Esta lista sigue la guía "Montar el repositorio con Scrum" que usamos en Galezarzal.

## Código y proceso

- [x] Código actual subido a `main`.
- [x] Plantillas de Issues, plantilla de Pull Request y `CODEOWNERS` (`.github/`).
- [x] Documentación de Scrum en `docs/` (guía, DoD, DoR y plantillas de actas), plantilla de Gherkin en `features/` y script de etiquetas en `scripts/`.
- [x] Roles de Agora anotados en `docs/scrum.md`: Divis es Product Owner y el Scrum Master de Galezarzal rota entre Valentina, Cristian y Juan Cardona.

## Etiquetas

```bash
bash scripts/crear-labels.sh <usuario>/<nombre-del-repo>
```

- [x] Etiquetas creadas (`epic`, `user-story`, `tech-story`, `RF`, `RNF`, `bug`, `acta`, `cambio-de-diseño`, `requirement-request` y las de prioridad).

## Tag de la línea base

- [x] Tag `v1.0-baseline` creado desde Releases sobre `main`, antes de proteger la rama y antes del Sprint 1.

## Protección de `main`

En Settings, Rules, Rulesets, nueva regla para la rama por defecto. Se hace después de subir todo lo anterior.

Ruleset `proteger-main`, activo:

- [x] Exigir Pull Request antes de fusionar, con al menos una aprobación.
- [x] Exigir revisión de los Code Owners, para que solo aprueben los que están en `.github/CODEOWNERS`.
- [x] Bloquear los force push y el borrado de la rama.

## Project (tablero Kanban)

Proyecto "Agora - Tablero Scrum", público.

- [x] Columnas del campo Status: Backlog, Sprint Backlog, In Progress, In Review y Done.
- [ ] Campos: Sprint (Iteration, por ahora de 2 semanas; se ajusta cuando se confirme la duración), Story Points (número), Prioridad (Alta, Media, Baja) y Tipo (Épica, Historia de usuario, Historia técnica, Bug, Acta). Ya están Sprint y Tipo; falta renombrar Estimate a Story Points y ajustar Priority a Prioridad (Alta, Media, Baja).
- [x] Workflows: item agregado va a Backlog; item cerrado va a Done; pull request fusionado va a Done.
- [x] Agregar automáticamente al Project los Issues nuevos del repo.
- [x] Vistas: Board para el Kanban, Table para el Product Backlog y Roadmap para los sprints.

## Colaboradores

El repositorio es de una cuenta personal, así que todos los colaboradores entran con permiso de escritura. Solo aprueban los Code Owners.

- [x] Invitaciones enviadas a Galezarzal (`mihzuk`, `Johan-v-p`, `Josdaver3000`, `lizarazo2005`) y a Agora (`montanovalentina-cyber`, `cristianfelipearango-cmyk`, `Juacoelseco`; el dueño es `divis-smith`).
- [x] Los mismos con rol Write en el Project.
- [ ] Que cada persona acepte su invitación al repositorio (`https://github.com/<usuario>/<repo>/invitations`). Faltan `Johan-v-p`, `Juacoelseco`, `lizarazo2005` y `montanovalentina-cyber`.
- [x] El profe ve el repositorio y el Project porque son públicos.

## Primer sprint

- [x] Roles definidos y anotados en `docs/scrum.md`.
- [ ] Épicas e historias creadas como Issues con las plantillas (el punto de partida está en `docs/backlog-inicial.md`).
- [ ] Sprint Planning hecho y su acta subida a `docs/actas/`.
