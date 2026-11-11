# Arquitectura y paquetes

Es una aplicación web en Python con Flask, sin base de datos externa (SQLite en `data/agora.db`), con mensajería en tiempo real por Socket.IO. El navegador recibe páginas HTML generadas con Jinja2 y archivos estáticos (CSS y JS) organizados por módulo.

```mermaid
flowchart TB
    B[Navegador: móvil o escritorio]

    subgraph FRONT[frontend/]
        direction LR
        TPL[templates/<br/>una carpeta por módulo<br/>+ compartidos/base.html]
        STA[static/<br/>css y js por módulo<br/>+ uploads/ de imágenes]
    end

    subgraph BACK[backend/ · Flask]
        direction TB
        APP[aplicacion.py · app.py<br/>crea la app y registra los Blueprints]
        subgraph RUT[rutas/ · capa HTTP]
            direction LR
            R1[autenticacion · ajustes]
            R2[publicaciones · portafolio]
            R3[foros · eventos]
            R4[social · mensajes]
            R5[moderacion · decoradores]
        end
        subgraph SER[servicios/ · consultas y reglas]
            direction LR
            S1[cuentas · publicaciones]
            S2[portafolio · foros · eventos]
            S3[social · mensajes · moderacion]
        end
        subgraph NUC[nucleo/ · utilidades compartidas]
            direction LR
            N1[base_datos · configuracion]
            N2[imagenes · utilidades]
        end
        RT[tiempo_real.py<br/>eventos de Socket.IO]
    end

    DB[(SQLite<br/>21 tablas)]

    B -->|HTTP| APP
    B <-->|WebSocket| RT
    APP --> RUT
    RUT --> SER
    SER --> NUC
    NUC -->|sqlite3| DB
    RUT -->|render_template| TPL
    TPL --> STA
    RUT --> RT
```

## Cosas que tener en cuenta
- Cada módulo funcional tiene un Blueprint en `backend/rutas/`, un servicio en `backend/servicios/` (con las consultas SQL) y su carpeta en `frontend/templates/` y `frontend/static/`. Así se agrega un módulo sin tocar el núcleo (RNF-05).
- La configuración viene de variables de entorno (`SECRET_KEY`, `DATABASE_PATH`, `FLASK_DEBUG`); la aplicación no lee el archivo `.env` por sí sola.
- Las imágenes subidas se validan, se vuelven a codificar con Pillow y se guardan en `frontend/static/uploads/` (que Git ignora).
- Los roles son estudiante, moderador y administrador (columna `usuarios.rol`). `before_request` expulsa las sesiones de cuentas suspendidas.
- Los tests (`tests/`) y el workflow de CI (`.github/workflows/tests.yml`) corren con `unittest`.
