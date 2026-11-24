# NODO — Foro multiusuario para taller H4cknet

Foro de aspecto realista con registro, login, posts, comentarios y contenido inicial. Dos superficies de Stored XSS intencionales: cuerpo de posts y cuerpo de comentarios (no títulos).

Ejecuta `docker compose up --build -d` y visita `http://localhost:8080`. Para acceso desde tu LAN: `http://IP_DEL_SERVIDOR:8080`, en una red de prácticas aislada. **No lo publiques en Internet.**

Consulta `GUIA_TALLER.md` para los ejemplos de JS, las explicaciones y el orden de los ejercicios. Ya NO se incluyen archivos JS de payloads. La interfaz ya no tiene panel `/lab` ni pantallas de simulación.

Hay usuarios ficticios iniciales con contraseñas de demostración en app.py; se pueden crear cuentas nuevas con `/register`. Usa solo contraseñas inventadas para el taller.

Si tienes una base de datos previa, Docker conserva las publicaciones en `foro-data`. Para borrarla `docker compose down -v` (elimina datos permanentemente).

## Seguridad
Esta app usa `|safe` de manera intencionadamente incorrecta en dos campos. No reutilices este patrón en producción. Las sesiones reales son `HttpOnly`; el token `h4cknet_demo_token` es un señuelo. No utilices el laboratorio para capturar credenciales o teclas privadas.
