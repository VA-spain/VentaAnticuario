# Venta Anticuario

Web de una tienda de antigüedades alemanas: catálogo de piezas con fotos, inicio de sesión y
página «Sobre nosotros».

## Cómo está hecha

| Pieza | Carpeta | Tecnología |
| --- | --- | --- |
| Web | `frontend/` | Next.js 16, TypeScript, Tailwind CSS |
| API | `backend/` | Python 3.12, FastAPI, SQLAlchemy |
| Base de datos | `docker-compose.yml` | MySQL 8.4 en un contenedor Docker |

El navegador solo habla con Next.js. Next.js pide los datos al backend en Python, y el backend
es el único que toca MySQL.

```
navegador ──▶ Next.js (3000) ──▶ backend Python (8000) ──▶ MySQL en Docker (3306)
```

## Páginas

| Ruta | Qué muestra |
| --- | --- |
| `/` | El catálogo: piezas en venta con foto, época, origen, descripción y precio |
| `/login` | Inicio de sesión con email y contraseña |
| `/signed-in` | «Has iniciado sesión correctamente». Solo se ve con una sesión válida |
| `/about` | Sobre nosotros y créditos de las fotografías |

## Puesta en marcha

Hace falta [Docker](https://www.docker.com/), [uv](https://docs.astral.sh/uv/) y Node.js 20 o
superior.

1. Crea tu fichero de claves a partir del ejemplo y cambia los valores:

   ```bash
   cp .env.example .env
   ```

2. Levanta MySQL:

   ```bash
   docker compose up -d
   ```

3. Crea las tablas y carga el catálogo y el usuario de prueba:

   ```bash
   cd backend && uv run python -m app.cli init-db
   ```

4. Arranca el backend (queda en http://127.0.0.1:8000, con la documentación de la API en `/docs`):

   ```bash
   cd backend && uv run uvicorn app.main:app --reload
   ```

5. En otra terminal, arranca la web (queda en http://localhost:3000):

   ```bash
   cd frontend && npm install && npm run dev
   ```

## Usuarios

No hay página de registro: los usuarios se crean desde la línea de comandos, en `backend/`.

- **Usuario de prueba.** `init-db` crea el usuario `DEMO_USER_EMAIL` con la contraseña
  `DEMO_USER_PASSWORD` del `.env`. Si cambias la contraseña en el `.env`, vuelve a lanzar
  `init-db`.
- **Crear un usuario.** Pide la contraseña sin mostrarla en pantalla:

  ```bash
  uv run python -m app.cli create-user cliente@ejemplo.com --name "Nombre Apellido"
  ```

- **Cambiar una contraseña.** Además cierra las sesiones abiertas de ese usuario:

  ```bash
  uv run python -m app.cli set-password cliente@ejemplo.com
  ```

## Cómo se protege el inicio de sesión

- **Contraseñas.** En MySQL solo se guarda su hash Argon2id, con una sal aleatoria por usuario.
  No es reversible: ni con acceso a la base de datos se puede recuperar una contraseña.
- **Sesiones.** Al entrar se genera un token aleatorio que viaja en una cookie `httpOnly` (el
  JavaScript de la página no puede leerla), `SameSite=Lax` y, en producción, solo por HTTPS. En
  MySQL se guarda el SHA-256 del token, no el token. La sesión dura 8 horas
  (`SESSION_TTL_MINUTES`) y se borra al cerrar sesión.
- **Sin pistas.** Un email que no existe y una contraseña equivocada reciben la misma respuesta y
  tardan lo mismo.
- **Freno de intentos.** Tras 5 fallos en 15 minutos desde una misma dirección contra una cuenta,
  hay que esperar; y hay un tope de 20 fallos por cuenta vengan de donde vengan. El contador vive
  en la memoria del backend: vale mientras corra en un solo proceso.
- **Claves.** Las de MySQL y la del usuario de prueba están en `.env`, que no se sube al
  repositorio. MySQL solo escucha en `127.0.0.1`.

## Catálogo y fotografías

- El catálogo está en `backend/data/products.json`. `init-db` crea las piezas que falten y
  actualiza las que ya existan; nunca borra. El orden en la web es el orden del fichero.
- **Es un catálogo de muestra**: las piezas, descripciones y precios son orientativos.
- Las fotos están en `frontend/public/products/`. Proceden de Wikimedia Commons y son de dominio
  público o de licencia Creative Commons; solo se han redimensionado. El autor, la licencia y el
  enlace al original de cada una están en `products.json` y se muestran en `/about`. Las fotos con
  licencia CC BY o CC BY-SA obligan a mantener ese crédito.

## Comprobaciones

```bash
cd backend && uv run pytest && uv run ruff check .
```

```bash
cd frontend && npm run lint && npx tsc --noEmit && npm run build
```

Los tests del backend usan una base de datos en memoria: no necesitan Docker ni tocan MySQL.

## Parar la base de datos

```bash
docker compose stop
```

`docker compose down -v` borra además todos los datos.
