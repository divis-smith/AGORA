# Ágora

Ágora es una red social universitaria para la comunidad de la Universidad del Valle, Seccional Zarzal. Centraliza lo que hoy se reparte entre grupos de chat, redes genéricas y correos sueltos: publicar contenido, resolver dudas académicas en foros, mostrar proyectos, enterarse de los eventos de la universidad y escribirse entre estudiantes, con moderadores que supervisan las normas de la comunidad.

## Qué se puede hacer

Hay tres roles: estudiante, moderador y administrador.

**Estudiantes.** Crean una cuenta y entran con correo y contraseña. En el feed publican (con imagen opcional, de forma anónima si quieren), reaccionan, comentan y filtran por categoría. En los foros hacen preguntas, responden, votan las respuestas y marcan la correcta. Arman su portafolio de proyectos, siguen a otros estudiantes, buscan publicaciones, personas y foros desde Explorar, y consultan las tendencias. Crean eventos, se inscriben (con control de cupos) y ven los participantes. Se escriben mensajes privados en tiempo real, reciben notificaciones, editan su perfil, su correo y su contraseña, y tienen una sección de ayuda.

**Moderadores.** Revisan los reportes abiertos y los resuelven: ignorarlos, eliminar el contenido o suspender al usuario. Una cuenta suspendida pierde su sesión y no puede volver a entrar.

**Administradores.** Hoy tienen los mismos permisos que los moderadores (también pueden eliminar cualquier evento). Su panel de administración todavía no funciona.

Falta por hacer, entre otras cosas: verificar la cuenta y recuperar la contraseña, hashtags y visibilidad de las publicaciones, las preferencias de privacidad y apariencia, la gestión de usuarios y foros desde el panel de administración, y una interfaz para reportar contenido. Hoy `/admin` y `/reportes` responden con error. Todo eso está en el [backlog inicial](docs/backlog-inicial.md) y el estado de cada requerimiento en [`docs/requerimientos/`](docs/requerimientos/funcionales.md).

## Con qué está hecho

Python con Flask 3.1 y Flask-SocketIO (mensajes y avisos en tiempo real), SQLite como base de datos, Pillow para validar y redimensionar las imágenes, plantillas Jinja2 y HTML, CSS y JavaScript escritos a mano. Las pruebas usan `unittest` y corren en GitHub Actions en cada push y en cada Pull Request.

## Instalación en local

Necesitas Python (el CI usa la 3.13) y Git.

**1. Copia el proyecto y entra a la carpeta.**

```
git clone https://github.com/<usuario>/<repositorio>.git
cd <repositorio>
```

**2. Crea un entorno virtual e instala las dependencias.**

```
python -m venv .venv
```

Actívalo con `.venv\Scripts\activate` en Windows o con `source .venv/bin/activate` en Linux y macOS. Después:

```
pip install -r backend/requirements.txt
```

**3. Crea la base de datos con los datos de demostración.**

```
python scripts/crear_db.py
```

Esto crea `data/agora.db` con las tablas de `scripts/esquema.sql` y contenido de ejemplo. Si quieres empezar de cero, borra ese archivo y vuelve a ejecutar el comando.

**4. Arranca la aplicación.**

```
python backend/app.py
```

Abre http://localhost:5000 en el navegador. Te lleva al inicio de sesión.

### Cuentas de prueba

Los datos de `scripts/datos_demo.py` son inventados y solo sirven para trabajar en local. No los uses en un sitio publicado.

| Correo | Contraseña | Rol |
|---|---|---|
| `admin@agora.edu` | `admin123` | Administrador |
| `mod@agora.edu` | `mod123` | Moderador |
| `vale@correounivalle.edu` | `vale123` | Estudiante |
| `divis@correounivalle.edu` | `divis123` | Estudiante |
| `cris@correounivalle.edu` | `cris123` | Estudiante |

### Variables de entorno

La aplicación lee estas variables del entorno. **No carga el archivo `.env` por sí sola**: `.env.example` es solo una referencia de los nombres, así que si quieres cambiarlas, defínelas en tu terminal antes de arrancar.

| Variable | Para qué sirve | Valor por defecto |
|---|---|---|
| `SECRET_KEY` | Firma las sesiones. Cámbiala por un valor aleatorio fuera de desarrollo. | `dev-only-change-me` |
| `DATABASE_PATH` | Ruta del archivo SQLite. | `data/agora.db` |
| `FLASK_DEBUG` | `1` activa el modo de depuración. | apagado |

## Pruebas

```
python -m unittest discover -s tests -v
```

Son 72 pruebas. Cubren reportes, suspensión de cuentas, ajustes de cuenta y subida de imágenes; todavía no hay pruebas de registro, foros, eventos, mensajes ni búsqueda.

## Estructura del proyecto

```
backend/
  app.py            punto de entrada
  aplicacion.py     crea la app y registra los módulos
  rutas/            capa HTTP: un Blueprint por módulo
  servicios/        consultas y reglas de cada módulo
  nucleo/           base de datos, configuración, imágenes y utilidades
  tiempo_real.py    eventos de Socket.IO
frontend/
  templates/        plantillas, una carpeta por módulo
  static/           CSS y JavaScript por módulo (y uploads/, que Git ignora)
scripts/            esquema.sql, crear_db.py y datos de demostración
tests/              pruebas con unittest
docs/               Scrum, requerimientos, diagramas y actas
features/           criterios de aceptación en Gherkin
```

## Equipo

Mantenemos el repositorio [@divis-smith](https://github.com/divis-smith), [@cristianfelipearango-cmyk](https://github.com/cristianfelipearango-cmyk), [@montanovalentina-cyber](https://github.com/montanovalentina-cyber) y [@Juacoelseco](https://github.com/Juacoelseco). El grupo de Galezarzal desarrolla sobre este repositorio y nosotros desarrollamos el suyo.

## Proceso Scrum y documentación

Trabajamos con Scrum y un tablero Kanban en GitHub Projects. Cómo lo hacemos, con las ceremonias y las plantillas, está en la carpeta `docs/`:

- [Cómo trabajamos con Scrum](docs/scrum.md): roles, ceremonias, tablero, Git y cambios de diseño.
- [Definition of Done](docs/DoD.md) y [Definition of Ready](docs/DoR.md).
- [Requerimientos funcionales](docs/requerimientos/funcionales.md) y [no funcionales](docs/requerimientos/no-funcionales.md).
- Diagramas en código (Mermaid): [entidad-relación](docs/diagramas/er.md), [clases](docs/diagramas/clases.md), [casos de uso](docs/diagramas/casos-de-uso.md), [secuencia](docs/diagramas/secuencia.md) y [arquitectura](docs/diagramas/arquitectura.md).
- [Colaboración entre grupos](docs/colaboracion-entre-grupos.md), [backlog inicial](docs/backlog-inicial.md) y [configuración de GitHub](docs/configuracion-github.md).
- Los diagramas originales de Desarrollo de Software I, en [draw.io](docs/legacy/Diagramas_ICONIX.drawio): descripción del problema, casos de uso, robustez, dominio, entidad-relación, paquetes y secuencia.
- Los criterios de aceptación en Gherkin están en [`features/`](features/) y las actas en [`docs/sprints/`](docs/sprints/).

Si un cambio modifica el diseño original, hay que actualizar los diagramas y la documentación en el mismo pull request.

## Cómo contribuir

La rama `main` está protegida: nadie sube cambios directo, todo entra con un pull request aprobado por un Code Owner. Trabajamos con una tarea por Issue, una rama y un pull request.

1. Elige un Issue del Backlog en el Project, asígnatelo y muévelo a In Progress.
2. Actualiza `main` y crea una rama nueva para la tarea:

   ```
   git switch main
   git pull origin main
   git switch -c feat/nombre-de-la-tarea
   ```

   Usamos `feat/...` para funciones nuevas, `fix/...` para correcciones, `refactor/...` y `chore/...` para mantenimiento, y `docs/...` para documentación.

3. Haz los cambios, corre las pruebas (`python -m unittest discover -s tests`) y sube la rama:

   ```
   git add .
   git commit -m "feat: descripción breve del cambio"
   git push -u origin feat/nombre-de-la-tarea
   ```

4. Abre un pull request hacia `main` y escribe en la descripción `Closes #número-del-issue`.
5. Espera la revisión. Si piden cambios, corrígelos en la misma rama y haz push; el pull request se actualiza solo.
6. Cuando lo aprueben y se una a `main`, borra la rama. Para la siguiente tarea crea una rama nueva (no reutilices la anterior) y siempre después de hacer `git pull` en `main`.
