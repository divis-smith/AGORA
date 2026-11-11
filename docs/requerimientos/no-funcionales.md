# Requerimientos no funcionales (línea base)

El documento de diagramas de Agora no trae requerimientos no funcionales, así que estos son una propuesta nuestra, escrita con las mismas categorías que usa Galezarzal y revisada contra el código. Hay que confirmarlos con el Product Owner y con el profe. Los nuevos siguen desde el RNF-08.

| ID | Categoría | Descripción | Cómo está hoy en el código |
|---|---|---|---|
| RNF-01 | Usabilidad | La interfaz debe ser intuitiva y funcionar bien desde el celular y desde el computador, dado que los estudiantes entran desde ambos. | Por verificar: `base.html` declara el viewport y 13 hojas de estilo usan `@media`, sin pruebas en dispositivos |
| RNF-02 | Disponibilidad | El sistema debe estar disponible al menos el 95 % del tiempo para que la comunidad consulte el contenido a cualquier hora. | Depende del despliegue; todavía no hay uno documentado |
| RNF-03 | Seguridad | Las contraseñas deben almacenarse cifradas con hash y el acceso a las funciones restringidas debe validarse según el rol de la cuenta. Las imágenes subidas deben validarse. | Se usa `generate_password_hash`, `login_required` y `moderador_required`; las sesiones de cuentas suspendidas se cierran; `nucleo/imagenes.py` valida el formato real, el tamaño (2 MB) y vuelve a codificar. Falta protección CSRF en los formularios y `SECRET_KEY` tiene un valor por defecto de desarrollo |
| RNF-04 | Rendimiento | La búsqueda y la carga del feed deben responder en menos de 3 segundos bajo uso normal. | Sin medición |
| RNF-05 | Escalabilidad | La arquitectura debe permitir agregar módulos nuevos sin afectar el núcleo. | Un Blueprint por módulo (`backend/rutas/`), servicios separados (`backend/servicios/`) y núcleo común (`backend/nucleo/`) |
| RNF-06 | Compatibilidad | El sistema debe funcionar en los navegadores actuales (Chrome, Firefox, Safari y Edge), en móvil y en escritorio. | Sin pruebas registradas |
| RNF-07 | Mantenibilidad | El código debe estar organizado en módulos independientes y tener pruebas automáticas que corran en cada cambio. | 72 tests con `unittest` y un workflow de CI (`.github/workflows/tests.yml`); los tests cubren reportes, suspensión, ajustes e imágenes de publicaciones y portafolio; no hay tests de registro, foros, eventos, mensajes ni búsqueda |
