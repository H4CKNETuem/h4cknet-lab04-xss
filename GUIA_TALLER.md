# Taller de XSS — NODO (H4cknet)

## Despliegue
`docker compose up --build -d` — abre `http://localhost:8080` y, desde otros equipos en una red controlada, `http://IP_DEL_SERVIDOR:8080`.

**IMPORTANTE:** entorno intencionadamente vulnerable. Solo red aislada autorizada, nunca Internet; cuentas y contraseñas inventadas. No existe panel `/lab` ni receptor de telemetría.

## Uso del foro
- Crea una cuenta en `/register` o entra con una cuenta ficticia ya sembrada.
- Pulsa «Crear publicación», elige título y escribe el cuerpo.
- Abre cualquier tema y escribe respuestas.
- **Ambos cuerpos son deliberadamente vulnerables** a XSS almacenado; los títulos y extractos de portada se escapan.
- El registro de usuarios y el inicio de sesión siguen siendo funcionales.

## Secuencia de clase (75 minutos)
1. 0–10 min: qué es el DOM, HTML frente a JavaScript, entrada no confiable.
2. 10–20 min: `alert(1)` en un comentario; comprobar ejecución en otro navegador.
3. 20–30 min: mismo ejercicio en el cuerpo de una publicación; observar que el título es distinto.
4. 30–40 min: modificar el título visible (`document.title`) y agregar una marca visual al DOM.
5. 40–55 min: leer `document.cookie` para mostrar el token DEMO; comprobar que la cookie de sesión, con `HttpOnly`, no aparece.
6. 55–65 min: explicación conceptual de eventos de teclado y su abuso; demostración de texto sintético en un campo controlado.
7. 65–75 min: reparar `|safe` en `templates/post.html` y repetir pruebas.

## Ejemplos para escribir EN CLASE (no son archivos JS precargados)

**Ejecución mínima:** `<script>alert('Hola, NODO')</script>`

**Cambio de título:** `<script>document.title='Mensaje cambiado desde un comentario'</script>`

**Estilo del sitio:** `<script>document.body.style.outline='6px solid orange'</script>`

**Cookie visible:** `<script>alert(document.cookie)</script>`

**Inspección de la cookie señuelo (sin transmisión):** `document.cookie` permite identificar el token ficticio `h4cknet_demo_token`. La sesión de Flask sigue protegida con `HttpOnly`.

**Prueba de `script src` alojado en el propio laboratorio:** crea un fichero sencillo `static/demo.js` con `alert('Código externo cargado');`, reconstruye con `docker compose up --build -d` y publica `<script src="/static/demo.js"></script>`.

## Matices docentes
- `document.cookie` no devuelve cookies `HttpOnly`.
- Ningún participante debe introducir claves personales ni activar capturas encubiertas.
- El cuerpo vulnerable se representa con `{{ post.body|safe }}` y `{{ c.body|safe }}`. Para arreglarlo cambia ambos a `{{ post.body }}` y `{{ c.body }}`.
- El código malicioso puede afectar a *cualquier* visitante que abra el tema.

## Si ya usaste la versión anterior
El volumen `foro-data` conserva los usuarios y publicaciones antiguas. Para empezar de cero: `docker compose down -v` y luego `docker compose up --build -d`. **Esto borra el contenido previo del foro.**
