# Venta Anticuario

Tienda online de antigüedades alemanas: catálogo con fotos, cuentas de cliente con su propio
portal (compras, favoritos y configuración), compra con un clic, panel de administración y
página de contacto.

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

| Ruta | Quién | Qué muestra |
| --- | --- | --- |
| `/` | Todos | Catálogo. «Comprar» y el corazón de favoritos piden iniciar sesión si no la hay |
| `/about` | Todos | Sobre nosotros y créditos de las fotografías |
| `/contact` | Todos | Formulario de contacto (se valida en el navegador y se guarda en MySQL) |
| `/register` | Todos | Alta: nombre de usuario (comprueba al vuelo si ya existe) y contraseña |
| `/login` | Todos | Inicio de sesión con nombre de usuario y contraseña |
| `/signed-in` | Con sesión | «Has iniciado sesión correctamente» y accesos al portal |
| `/account` | Clientes | Portal: resumen de la cuenta |
| `/account/orders` | Clientes | Las piezas compradas |
| `/account/favorites` | Clientes | Las piezas marcadas como favoritas |
| `/account/settings` | Clientes | Nombre, apellidos, correo, pasaporte y tarjeta (número, caducidad y CVV) |
| `/admin` | Administradores | Todos los usuarios, con acceso al portal de cada uno |
| `/admin/users/NOMBRE/...` | Administradores | El portal de ese usuario, pudiendo modificar pedidos, favoritos y datos |

Al registrarse, la cuenta queda creada, la sesión iniciada y el usuario llega a su portal. Una
compra es un clic en «Comprar»: crea el pedido al precio de ese momento y lleva a «Mis compras».
De momento el stock es ilimitado y no hay página de pago.

## Puesta en marcha

Hace falta [Docker](https://www.docker.com/), [uv](https://docs.astral.sh/uv/) y Node.js 20 o
superior.

1. Crea tu fichero de claves a partir del ejemplo y rellénalo (incluidas las contraseñas del
   cliente de prueba y del administrador):

   ```bash
   cp .env.example .env
   ```

2. Levanta MySQL:

   ```bash
   docker compose up -d
   ```

3. Crea las tablas y carga el catálogo y los usuarios de prueba:

   ```bash
   cd backend && uv run python -m app.cli init-db
   ```

   Si vienes de la primera versión (login por email), la base tiene otras tablas: bórrala y
   créala de nuevo con `uv run python -m app.cli reset-db --yes` (borra todos los datos).

4. Arranca el backend (queda en http://127.0.0.1:8000, con la documentación de la API en `/docs`):

   ```bash
   cd backend && uv run uvicorn app.main:app --reload
   ```

5. En otra terminal, arranca la web (queda en http://localhost:3000):

   ```bash
   cd frontend && npm install && npm run dev
   ```

## Usuarios

- **Clientes**: se dan de alta solos en `/register`. El nombre de usuario tiene de 3 a 30
  caracteres, empieza por una letra y solo usa letras, números, punto, guion y guion bajo; no
  distingue mayúsculas. La contraseña, al menos 8 caracteres.
- **Usuarios de prueba**: `init-db` crea el cliente `DEMO_USER_USERNAME` y el administrador
  `ADMIN_USERNAME` del `.env`, con sus contraseñas (`DEMO_USER_PASSWORD` y `ADMIN_PASSWORD`). Si
  cambias una contraseña en el `.env`, vuelve a lanzar `init-db`.
- **Más administradores** (pide la contraseña sin mostrarla), desde `backend/`:

  ```bash
  uv run python -m app.cli create-user NOMBRE --admin
  ```

- **Cambiar una contraseña**:

  ```bash
  uv run python -m app.cli set-password NOMBRE
  ```

## La sesión

La sesión es una cookie `va_session`, `HttpOnly` y `SameSite=Lax`, que dura 8 horas
(`SESSION_TTL_MINUTES`). Su valor es:

- cliente: `nombre+0987654321`
- administrador: `0987654321+nombre`

El backend lee el nombre de la cookie y decide: la cookie de administrador solo vale si ese usuario
es administrador en la base de datos, y cada cliente solo ve y cambia sus propios datos. Las rutas
`/session/login` y `/session/register` de Next.js escriben la cookie a mano, porque la función
estándar de Next.js codificaría el `+` como `%2B`.

## Base de datos

Las tablas están en [backend/app/models.py](backend/app/models.py):

| Tabla | Qué guarda |
| --- | --- |
| `products` | El catálogo (se carga desde [backend/data/products.json](backend/data/products.json)) |
| `users` | Clientes y administradores: nombre de usuario, hash de la contraseña, rol y los datos de configuración |
| `orders` | Un pedido por cada clic en «Comprar»: pieza, cantidad, precio de ese momento y estado |
| `favorites` | Las piezas favoritas de cada usuario |
| `contact_messages` | Los mensajes de la página de contacto |

## Pendiente de seguridad (a propósito, por ahora)

Esta versión prioriza ir rápido. Antes de que la usen clientes reales hay que resolver esto:

- **La cookie se puede fabricar.** No lleva firma ni ningún secreto: quien conozca un nombre de
  usuario puede entrar como él escribiendo `nombre+0987654321` en su navegador, y como
  administrador con `0987654321+admin`. Hay que sustituirla por una sesión aleatoria o firmada.
- **Datos de pago y pasaporte en claro.** El número de tarjeta, la caducidad, el CVV y el pasaporte
  se guardan tal cual en MySQL y se muestran en la configuración. Las normas de las tarjetas
  (PCI DSS) prohíben guardar el CVV en ningún caso. Al hacer la página de pago, lo correcto es
  delegar en una pasarela (Stripe, Redsys…) y quitar estas columnas.
- **El contacto solo se valida en el navegador.** El backend solo comprueba longitudes.
- **Sin HTTPS en local.** En producción la cookie se marca `Secure` y hace falta HTTPS.
- **El freno de intentos de login vive en memoria**: vale con un solo proceso de backend.

Lo que sí está: las contraseñas se guardan con hash Argon2id (no se pueden recuperar ni con acceso
a la base de datos) y el login responde igual tanto si el usuario no existe como si la contraseña
es incorrecta.

## Catálogo y fotografías

- El catálogo está en `backend/data/products.json`. `init-db` crea las piezas que falten y
  actualiza las que ya existan; nunca borra. El orden en la web es el orden del fichero.
- **Es un catálogo de muestra**: las piezas, descripciones y precios son orientativos.
- Las fotos están en `frontend/public/products/`. Proceden de Wikimedia Commons y son de dominio
  público o de licencia Creative Commons; solo se han redimensionado. El autor, la licencia y el
  enlace al original de cada una se muestran en `/about`. Las fotos con licencia CC BY o CC BY-SA
  obligan a mantener ese crédito.

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
