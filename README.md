# Hotel Django

Sistema web de gestión hotelera desarrollado con Django para administrar habitaciones, reservas, usuarios, pagos simulados y reportes operativos.

## Descripción del proyecto

El proyecto cubre el ciclo principal de operación de un hotel:

- Registro y verificación de usuarios por correo.
- Gestión de habitaciones y tipos de habitación.
- Búsqueda de disponibilidad por fechas.
- Carrito y checkout de reservas.
- Simulación de pago con HotelPay.
- Cancelación con políticas de reembolso.
- Dashboard administrativo y reportes en PDF.

La interfaz está construida con plantillas Django y Bootstrap.

## Tecnologías utilizadas

- Python 3.12 o compatible con Django 5.x.
- Django.
- SQLite para desarrollo.
- Gunicorn para producción.
- WhiteNoise para archivos estáticos.
- ReportLab para PDFs.
- Pillow para imágenes.
- python-decouple para variables de entorno.
- dj-database-url y psycopg2-binary para despliegue con PostgreSQL.

## Funcionalidades principales

- Registro de usuarios con verificación de correo.
- Login y logout.
- Roles de administrador y cliente.
- Gestión de habitaciones y tipos.
- Búsqueda de disponibilidad.
- Carrito de reservas.
- Checkout con pasarela simulada.
- Confirmación, rechazo y cancelación de reservas.
- Reportes filtrables y exportación PDF.

## Requerimientos

### Software

- Python 3.12 o superior.
- pip.
- Git.
- Base de datos SQLite para desarrollo.
- PostgreSQL recomendado para producción.

### Variables de entorno

Crear un archivo `.env` en la raíz del proyecto con valores similares a estos o copiar la plantilla `.env.example`:

```env
SECRET_KEY=tu-clave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://127.0.0.1:8000
API_URL=http://127.0.0.1:8000

DATABASE_URL=sqlite:///db.sqlite3

EMAIL_HOST=smtp.ejemplo.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_correo@ejemplo.com
EMAIL_HOST_PASSWORD=tu_contraseña
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=tu_correo@ejemplo.com
```

## Render y arquitectura desacoplada

El proyecto está preparado para Render bajo un esquema desacoplado por variables de entorno.

- Backend: servicio web Django en Render.
- Base de datos: PostgreSQL administrado en Render.
- Frontend externo: debe consumir el backend mediante `API_URL` o `VITE_API_URL` / `NEXT_PUBLIC_API_URL` / `REACT_APP_API_URL`.

Este repositorio actualmente no contiene una aplicación frontend separada con React, Vue o Next.js. La interfaz activa sigue siendo Django con plantillas, por lo que las variables de frontend quedan preparadas como plantilla para una separación futura o para otro repositorio frontend.

### Variables clave para Render

```env
DEBUG=False
ALLOWED_HOSTS=your-backend.onrender.com
FRONTEND_URL=https://your-frontend.onrender.com
BACKEND_URL=https://your-backend.onrender.com
API_URL=https://your-backend.onrender.com
DATABASE_URL=postgres://...
```

## Instalación paso a paso

### 1. Clonar o abrir el proyecto

Ubícate en la carpeta del proyecto:

```bash
cd HotelDjango/Hotel
```

### 2. Crear y activar entorno virtual

En Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias del backend

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea el archivo `.env` en la raíz del proyecto y define la clave secreta, hosts permitidos y credenciales de correo.

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

### 7. Ejecutar el servidor local

```bash
python manage.py runserver
```

## Frontend

El frontend no tiene un build independiente. Usa plantillas Django y recursos servidos por el backend.

### Instalación

No requiere instalación adicional fuera de las dependencias del backend.

### Configuración

- Las plantillas están en `templates/` y en las carpetas `templates/` de cada app.
- Bootstrap, Bootstrap Icons y Google Fonts se cargan por CDN.
- Las imágenes de habitaciones se almacenan en `media/`.

### Ejecución

Se renderiza automáticamente al levantar Django con `runserver` o con Gunicorn en producción.

## Configuración de base de datos

### Desarrollo

El proyecto viene configurado con SQLite en `db.sqlite3`.

### Producción

Recomendación: usar PostgreSQL y definir `DATABASE_URL` en el entorno.

### Variables necesarias

- `DATABASE_URL`
- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`

## Usuario administrador inicial

No existe un seed automático de superusuario en migraciones. El acceso administrativo debe crearse manualmente con:

```bash
python manage.py createsuperuser
```

La base local incluida contiene usuarios de ejemplo con rol `admin` o `cliente`, pero eso no reemplaza un superusuario de Django para acceder a `/admin/`.

## Scripts disponibles

### Desarrollo

```bash
python manage.py runserver
```

### Producción

El `Procfile` del proyecto usa Gunicorn. El comando base apunta al módulo de WSGI del proyecto.

### Render

- Build command del backend: `pip install -r requirements.txt`
- Start command del backend: definido en `Procfile`
- Migraciones: se ejecutan en la fase `release` del `Procfile`
- Frontend separado: usar la variable `API_URL` para apuntar al backend desplegado

### Build

```bash
python manage.py collectstatic --noinput
```

### Tests

```bash
python manage.py test
```

### Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

## Troubleshooting

### No llega el correo de verificación

- Revisa las variables `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` y `DEFAULT_FROM_EMAIL`.
- Verifica que el proveedor SMTP permita el envío desde tu entorno.

### Error con la base de datos

- Confirma que `DATABASE_URL` es válido.
- Ejecuta `python manage.py migrate` después de cambiar de entorno.

### Las imágenes no cargan

- Asegúrate de que `MEDIA_ROOT` y `MEDIA_URL` estén correctamente configurados.
- En desarrollo, Django sirve archivos media cuando `DEBUG=True`.

### No puedo entrar al panel admin

- Crea un superusuario con `createsuperuser`.
- Verifica que la cuenta tenga `is_staff=True`.

### Los reportes PDF fallan

- Verifica que `reportlab` esté instalado.
- Confirma que existan datos y filtros válidos para generar el informe.

### La verificación de correo abre un enlace incorrecto

- Revisa la configuración de URL base en el servicio de correo.
- No dejes URLs de localhost hardcodeadas en producción.

# Hotel-Django

Sistema de gestión hotelera desarrollado con Django.

## Sistema de Autenticación

### Rutas

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/auth/register/` | GET, POST | Registro de nuevos usuarios |
| `/auth/login/` | GET, POST | Inicio de sesión |
| `/auth/logout/` | GET | Cierre de sesión |
| `/auth/verify/?token=UUID` | GET | Verificación de correo electrónico |
| `/auth/email-sent/` | GET | Confirmación de envío de correo |
| `/auth/` | GET | Home (requiere autenticación) |

### Flujo de Autenticación

1. El usuario se registra en `/auth/register/`
2. El sistema crea un token de verificación (UUID) asociado al usuario
3. Se envía un correo electrónico con el enlace de verificación
4. El usuario hace clic en el enlace (`/auth/verify/?token=UUID`)
5. El sistema valida el token (existencia, expiración de 24h, uso previo)
6. Si es válido, la cuenta se activa (`is_active=True`, `is_verified=True`)
7. El usuario puede iniciar sesión en `/auth/login/`

### Roles

| Rol | Descripción |
|-----|-------------|
| `admin` | Administrador del sistema con acceso a funciones de gestión |
| `cliente` | Cliente del hotel con acceso a su zona personal |

El rol se selecciona durante el registro y se muestra en la interfaz (navbar y home).

### Configuración de Correo

En desarrollo se utiliza `console.EmailBackend`, que imprime los correos en la terminal en lugar de enviarlos.

Para configurar un servidor de correo real, crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
EMAIL_HOST=smtp.ejemplo.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_correo@ejemplo.com
EMAIL_HOST_PASSWORD=tu_contraseña
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=tu_correo@ejemplo.com
```

### Protección de Rutas

- La vista `home` está protegida con `@login_required`
- Si un usuario no autenticado intenta acceder, es redirigido a `/auth/login/`
- El login valida que el usuario haya verificado su correo antes de permitir el acceso

### Verificación de Token

- Los tokens expiran después de **24 horas**
- Un token solo puede ser utilizado **una vez**
- Los tokens no se eliminan de la base de datos (se marcan como usados)
- Si el token es inválido, expirado o usado, se muestra un mensaje de error claro

## Ejecución del Proyecto

```bash
# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Ejecutar servidor de desarrollo
python manage.py runserver
```

## Tecnologías

- Python 3.x
- Django 5.2
- Bootstrap 5.3
- SQLite (desarrollo)

# Documentación técnica del sistema de gestión y reservas de hotel

## 1. Descripción general del sistema

El sistema es una aplicación web desarrollada con Django para la gestión de un hotel. Permite administrar habitaciones, tipos de habitación, reservas, pagos simulados, políticas de cancelación, verificación de usuarios por correo y generación de reportes en PDF.

### Objetivo del sistema

Centralizar en una sola plataforma la operación de reservas del hotel, la gestión interna del catálogo de habitaciones y la supervisión administrativa mediante un panel con métricas y reportes.

### Problema que resuelve

Evita llevar el control de disponibilidad, reservas, clientes y reportes de forma manual o dispersa en hojas de cálculo. La aplicación formaliza el flujo completo desde el registro del cliente hasta la confirmación o cancelación de una reserva.

### Alcance del proyecto

El alcance actual cubre:

- Registro y autenticación de usuarios con verificación por correo.
- Gestión de usuarios con roles `admin` y `cliente`.
- Administración de tipos de habitación y habitaciones.
- Búsqueda de disponibilidad por fechas y capacidad.
- Carrito de reservas en sesión.
- Checkout con pasarela simulada `HotelPay`.
- Cancelación de reservas con políticas de reembolso.
- Dashboard de administración con métricas y actividad reciente.
- Reportes filtrables y exportación a PDF.

No existe un módulo de marketplace/inventario independiente ni una API REST pública; la aplicación es principalmente renderizada por plantillas Django.

### Tipo de usuarios del sistema

- Administrador: gestiona habitaciones, tipos, reservas, reportes y métricas.
- Cliente: consulta disponibilidad, crea reservas, revisa su historial y cancela reservas permitidas.

### Funcionalidades principales

- Registro de usuario con validación de correo.
- Inicio y cierre de sesión.
- Listado y detalle de habitaciones.
- Gestión CRUD de tipos de habitación.
- Búsqueda de disponibilidad por fechas, tipo y capacidad.
- Carrito de reservas basado en sesión.
- Checkout con pago simulado.
- Confirmación o rechazo de reservas según el resultado del pago.
- Cancelación con cálculo de reembolso.
- Panel administrativo con indicadores y actividad reciente.
- Reportes de reservas, clientes y habitaciones en pantalla y en PDF.

## 2. Arquitectura del sistema

### Arquitectura general del proyecto

El proyecto sigue una arquitectura Django clásica MVT, organizada por apps funcionales:

- `authapp`: autenticación, registro y verificación de correo.
- `habitaciones`: catálogo y disponibilidad de habitaciones.
- `reservas`: carrito, checkout, pagos simulados, cancelaciones y consulta de reservas.
- `reportes`: dashboard administrativo, filtros y exportación PDF.

La interfaz se construye con plantillas Django y Bootstrap 5.3. El backend usa vistas server-side, modelos ORM y formularios Django.

### Tecnologías utilizadas

- Backend: Python, Django 5.x.
- Frontend: plantillas Django, Bootstrap 5.3, Bootstrap Icons y Google Fonts.
- Base de datos: SQLite en el estado actual del proyecto.
- PDF: ReportLab.
- Imágenes: Pillow.
- Despliegue: Gunicorn, WhiteNoise, dj-database-url y python-decouple.

### Estructura de carpetas del proyecto

```text
Hotel/
  manage.py
  procfile
  requirements.txt
  db.sqlite3
  .env
  Hotel/
    settings.py
    urls.py
    wsgi.py
    asgi.py
  authapp/
    models.py
    forms.py
    views.py
    services.py
    urls.py
    migrations/
    templates/
  habitaciones/
    models.py
    forms.py
    views.py
    urls.py
    migrations/
    templates/
  reservas/
    models.py
    forms.py
    views.py
    cart.py
    gateway.py
    context_processors.py
    urls.py
    migrations/
    templates/
  reportes/
    forms.py
    services.py
    views.py
    urls.py
    templates/
  templates/
    base.html
    authapp/
  static/
  media/
```

### Explicación de módulos y responsabilidades

- `authapp`: define el usuario personalizado, el token de verificación y el flujo de login/registro.
- `habitaciones`: administra tipos, habitaciones, imágenes, disponibilidad y validaciones de capacidad.
- `reservas`: controla el carrito, el checkout, la lógica de pago simulada y la cancelación con reembolso.
- `reportes`: calcula métricas, organiza datos analíticos y genera PDFs.
- `templates/base.html`: layout general, navegación, estilos base y mensajes del sistema.

## 3. Modelos del sistema

### 3.1 `CustomUser`

**Propósito:** reemplaza el usuario estándar de Django para agregar roles y estado de verificación.

**Campos:**

- `username`: `CharField`, único.
- `password`: heredado de `AbstractUser`.
- `email`: `EmailField`.
- `role`: `CharField` con valores `admin` y `cliente`.
- `is_verified`: `BooleanField` que indica si el correo fue confirmado.

**Relaciones:**

- Hereda de `AbstractUser`.
- Relación M2M con grupos y permisos de Django.

**Restricciones y validaciones:**

- El rol se limita a las opciones definidas en `ROLE_CHOICES`.
- El login exige que `is_verified = True`.

### 3.2 `EmailVerificationToken`

**Propósito:** almacenar el token enviado por correo para confirmar la cuenta.

**Campos:**

- `user`: `ForeignKey` hacia `CustomUser`.
- `token`: `UUIDField`, único.
- `created_at`: `DateTimeField` automático.
- `is_used`: `BooleanField`.

**Relaciones:**

- Un usuario puede tener varios tokens de verificación.

**Restricciones y validaciones:**

- El token expira funcionalmente a las 24 horas.
- Solo puede utilizarse una vez.

### 3.3 `TipoHabitacion`

**Propósito:** clasificar habitaciones por categoría.

**Campos:**

- `nombre`: `CharField`, único.
- `descripcion`: `TextField` opcional.

**Relaciones:**

- Un tipo tiene muchas habitaciones.

**Restricciones:**

- Se ordena alfabéticamente por `nombre`.

### 3.4 `Habitacion`

**Propósito:** representar una habitación reservable del hotel.

**Campos:**

- `numero`: `CharField`, único.
- `tipo`: `ForeignKey` hacia `TipoHabitacion` con `PROTECT`.
- `capacidad`: `PositiveIntegerField`.
- `precio_por_noche`: `DecimalField`.
- `estado`: `CharField` con valores `disponible`, `ocupada` y `mantenimiento`.
- `descripcion`: `TextField` opcional.
- `imagen`: `ImageField` opcional.
- `activa`: `BooleanField` para borrado lógico.
- `fecha_creacion`: `DateTimeField` automático.
- `fecha_actualizacion`: `DateTimeField` automático.

**Relaciones:**

- Pertenece a un tipo de habitación.
- Tiene múltiples reservas asociadas.

**Restricciones y validaciones:**

- El número de habitación es único.
- No puede eliminarse físicamente un tipo si tiene habitaciones asociadas.
- La capacidad se valida también en el formulario de reserva.

### 3.5 `PoliticaCancelacion`

**Propósito:** definir reglas de reembolso por anticipación de cancelación.

**Campos:**

- `nombre`: `CharField`.
- `dias_anticipacion`: `PositiveIntegerField`.
- `porcentaje_reembolso`: `DecimalField`.
- `activa`: `BooleanField`.

**Relaciones:**

- Se usa de forma lógica para calcular reembolsos; no depende de una relación directa con `Reserva`.

**Restricciones y validaciones:**

- Las reglas activas se evalúan por orden descendente de días de anticipación.

### 3.6 `Reserva`

**Propósito:** registrar la reserva realizada por un cliente.

**Campos:**

- `codigo`: `CharField`, único, generado automáticamente.
- `usuario`: `ForeignKey` a `CustomUser`, opcional.
- `habitacion`: `ForeignKey` a `Habitacion` con `PROTECT`.
- `nombre_cliente`: `CharField`.
- `email_cliente`: `EmailField`.
- `telefono_cliente`: `CharField` opcional.
- `fecha_entrada`: `DateField`.
- `fecha_salida`: `DateField`.
- `huespedes`: `PositiveIntegerField`.
- `precio_por_noche`: `DecimalField`.
- `total`: `DecimalField`.
- `estado`: `CharField` con valores `pendiente`, `confirmada`, `cancelada` y `completada`.
- `fecha_creacion`: `DateTimeField` automático.
- `fecha_cancelacion`: `DateTimeField` opcional.
- `motivo_cancelacion`: `CharField` opcional.
- `monto_reembolsado`: `DecimalField`.

**Relaciones:**

- Cada reserva pertenece a una habitación.
- Puede vincularse al usuario autenticado que la creó.
- Puede tener un pago asociado.

**Restricciones y validaciones:**

- El código de reserva se genera automáticamente y se garantiza como único.
- La cancelación depende del estado y de la fecha de entrada.
- El método `puede_cancelarse` solo devuelve `True` para estados pendientes o confirmados con fecha futura.

### 3.7 `Pago`

**Propósito:** almacenar el resultado del pago simulado de una reserva.

**Campos:**

- `reserva`: `OneToOneField` hacia `Reserva`.
- `metodo`: `CharField` con valores `tarjeta` y `paypal`.
- `estado`: `CharField` con valores `aprobado` y `rechazado`.
- `referencia`: `CharField`, único.
- `titular`: `CharField` opcional.
- `ultimos_4`: `CharField` opcional.
- `monto`: `DecimalField`.
- `fecha`: `DateTimeField` automático.

**Relaciones:**

- Una reserva tiene un solo pago.

**Restricciones:**

- La referencia de pago debe ser única.

### 3.8 Entidades históricas o no activas

La migración inicial de `habitaciones` muestra una entidad histórica llamada `PrecioTemporada`, pero fue eliminada posteriormente mediante migración. No forma parte del modelo actual operativo.

## 4. Flujos funcionales del sistema

### 4.1 Autenticación

#### Registro

1. El usuario completa el formulario en `/auth/register/`.
2. Se valida que el nombre de usuario y el correo no estén repetidos.
3. Se valida la contraseña y su confirmación.
4. Se crea el usuario con `is_active=False` e `is_verified=False`.
5. Se genera un `EmailVerificationToken`.
6. Se envía el correo de verificación.

#### Verificación de correo

1. El usuario abre el enlace enviado por correo.
2. El sistema valida que el token sea un UUID válido.
3. Verifica que el token exista, no esté usado y no haya expirado.
4. Se activa el usuario y se marca `is_verified=True`.
5. El token se marca como utilizado.

#### Login

1. El usuario envía credenciales en `/auth/login/`.
2. Django autentica con el usuario personalizado.
3. Si el correo no fue verificado, el acceso se bloquea.
4. Si el usuario es válido y verificado, se inicia la sesión y se redirige al home.

#### Cierre de sesión

1. El usuario accede a `/auth/logout/`.
2. El sistema cierra la sesión y redirige al login.

#### Recuperación de contraseña

No existe un flujo de recuperación de contraseña implementado en el proyecto actual.

### 4.2 Roles y permisos

- `admin`: accede al dashboard, reportes, gestión de habitaciones y tipos.
- `cliente`: consulta habitaciones, reserva, revisa sus reservas y cancela las que correspondan.

La aplicación usa un decorador `admin_required` en varias vistas y valida el rol antes de permitir acciones sensibles.

### 4.3 Administración

#### Gestión de tipos de habitación

1. El administrador entra a `/habitaciones/tipos/`.
2. Puede crear, editar o eliminar tipos.
3. La eliminación se bloquea si existen habitaciones asociadas.

#### Gestión de habitaciones

1. El administrador entra a `/habitaciones/`.
2. Puede crear, editar o dar de baja lógica una habitación.
3. La baja lógica se ejecuta marcando `activa=False`.

#### Dashboard administrativo

1. El administrador accede a `/reportes/` o al home autenticado.
2. El sistema calcula métricas globales.
3. Se muestran reservas recientes, clientes recientes, cambios recientes y cancelaciones recientes.
4. El endpoint `/reportes/datos/` expone datos agregados para visualizaciones.

#### Configuración del sistema

La configuración se concentra en `Hotel/settings.py`, donde se definen apps instaladas, plantillas, base de datos, correo y archivos multimedia/estáticos.

### 4.4 Cliente

#### Búsqueda de disponibilidad

1. El cliente consulta `/habitaciones/buscar/`.
2. Envía fechas, tipo de habitación y capacidad mínima.
3. El sistema filtra habitaciones activas, disponibles y sin reservas solapadas.

#### Consulta de habitaciones

1. El cliente puede ver el listado de habitaciones en `/habitaciones/` y el listado alterno en `/reservas/habitaciones/`.
2. Cada habitación tiene detalle público.

#### Realización de reservas

1. El cliente agrega una habitación al carrito desde el detalle o el listado.
2. El carrito valida fechas y disponibilidad.
3. En checkout se capturan los datos del cliente.
4. Se crean reservas en estado `pendiente`.
5. Se abre la pasarela simulada `HotelPay`.
6. Tras el pago, la reserva pasa a `confirmada` o `cancelada`.

#### Gestión de perfil

No existe una pantalla de perfil editable separada. El usuario gestiona su experiencia desde el flujo de autenticación y sus reservas.

### 4.5 Marketplace

No existe un marketplace en este proyecto.

### 4.6 Reportes

#### Dashboard y reportes

1. El administrador accede al dashboard de reportes.
2. Puede filtrar reservas, clientes y habitaciones.
3. Puede exportar cada conjunto de datos a PDF.

#### Flujo de generación de reportes PDF

1. Se reciben filtros por query string.
2. Se construye un queryset filtrado.
3. Se transforman los datos a filas tabulares.
4. ReportLab genera el PDF en memoria.
5. El archivo se descarga como respuesta HTTP.

## 5. Rutas principales del sistema

### 5.1 Backend / vistas del sistema

| Ruta | Método | Descripción | Parámetros | Respuesta esperada | Autenticación |
|---|---|---|---|---|---|
| `/` | GET | Redirección al home autenticado | Ninguno | Redirige a `/auth/` | No |
| `/auth/` | GET | Home principal | Ninguno | Dashboard según rol | Sí |
| `/auth/register/` | GET, POST | Registro de usuario | Formulario de registro | Crea usuario y token | No |
| `/auth/login/` | GET, POST | Inicio de sesión | Usuario y contraseña | Sesión activa | No |
| `/auth/logout/` | GET | Cierre de sesión | Ninguno | Redirección al login | Sí |
| `/auth/email-sent/` | GET | Confirmación de correo enviado | Ninguno | Vista informativa | No |
| `/auth/verify/?token=...` | GET | Verificación de correo | Token UUID | Activa usuario | No |
| `/habitaciones/` | GET | Listado de habitaciones | Ninguno | Lista de habitaciones activas | No |
| `/habitaciones/<pk>/` | GET | Detalle de habitación | PK | Vista de detalle | No |
| `/habitaciones/tipos/` | GET | Listado de tipos | Ninguno | Lista de tipos | Sí |
| `/habitaciones/tipos/crear/` | GET, POST | Crear tipo | Formulario | Crea tipo | Sí, admin |
| `/habitaciones/tipos/<pk>/editar/` | GET, POST | Editar tipo | PK + formulario | Actualiza tipo | Sí, admin |
| `/habitaciones/tipos/<pk>/eliminar/` | GET, POST | Eliminar tipo | PK | Baja del tipo si no tiene dependencias | Sí, admin |
| `/habitaciones/crear/` | GET, POST | Crear habitación | Formulario | Crea habitación | Sí, admin |
| `/habitaciones/<pk>/editar/` | GET, POST | Editar habitación | PK + formulario | Actualiza habitación | Sí, admin |
| `/habitaciones/<pk>/eliminar/` | GET, POST | Baja lógica de habitación | PK | Marca `activa=False` | Sí, admin |
| `/habitaciones/buscar/` | GET | Búsqueda de disponibilidad | Fechas, tipo, capacidad | Lista filtrada | No |
| `/reservas/habitaciones/` | GET | Listado alterno de habitaciones disponibles | Ninguno | Lista de habitaciones disponibles | Sí |
| `/reservas/mis-reservas/` | GET | Reservas del usuario | Ninguno | Historial personal | Sí |
| `/reservas/carrito/` | GET | Detalle del carrito | Ninguno | Ítems y total | Sí |
| `/reservas/carrito/agregar/<habitacion_pk>/` | GET, POST | Agregar habitación al carrito | PK + fechas | Inserta ítem de carrito | Sí |
| `/reservas/carrito/quitar/<habitacion_pk>/` | POST | Quitar ítem del carrito | PK | Elimina ítem | Sí |
| `/reservas/carrito/vaciar/` | POST | Vaciar carrito | Ninguno | Limpia sesión | Sí |
| `/reservas/checkout/` | GET, POST | Confirmar datos y crear reservas pendientes | Datos cliente | Abre pasarela | Sí |
| `/reservas/hotelpay/<token>/` | GET, POST | Checkout de pasarela simulada | Token + datos de tarjeta | Procesa pago | Sí |
| `/reservas/hotelpay/callback/` | GET | Callback de pasarela | Token | Registra pago y actualiza reservas | Sí |
| `/reservas/hotelpay/<token>/resultado/` | GET | Resultado final del pago | Token | Éxito o rechazo | Sí |
| `/reservas/buscar/` | GET | Buscar reserva por código y correo | Código + email | Redirige al detalle | No |
| `/reservas/<codigo>/` | GET | Detalle público de reserva | Código | Vista de reserva | No |
| `/reservas/<codigo>/cancelar/` | GET, POST | Cancelar reserva propia | Código + motivo | Cancela y calcula reembolso | Sí |
| `/reportes/` | GET | Dashboard administrativo | Ninguno | Métricas y actividad | Sí, admin |
| `/reportes/datos/` | GET | Datos JSON para gráficas | Ninguno | JSON con agregados | Sí, admin |
| `/reportes/reservas/` | GET | Reporte filtrado de reservas | Filtros por fecha, estado, cliente, habitación | Listado analítico | Sí, admin |
| `/reportes/clientes/` | GET | Reporte filtrado de clientes | Filtros por fecha, estado, cliente | Listado analítico | Sí, admin |
| `/reportes/habitaciones/` | GET | Reporte filtrado de habitaciones | Filtros por fecha, estado, tipo | Listado analítico | Sí, admin |
| `/reportes/reservas/pdf/` | GET | Exportar reporte de reservas | Filtros por query string | PDF descargable | Sí, admin |
| `/reportes/clientes/pdf/` | GET | Exportar reporte de clientes | Filtros por query string | PDF descargable | Sí, admin |
| `/reportes/habitaciones/pdf/` | GET | Exportar reporte de habitaciones | Filtros por query string | PDF descargable | Sí, admin |

### 5.2 Frontend / pantallas principales

| Pantalla | Ruta | Propósito |
|---|---|---|
| Home autenticado | `/auth/` | Mostrar panel según rol. |
| Login | `/auth/login/` | Iniciar sesión. |
| Registro | `/auth/register/` | Crear cuenta. |
| Verificación | `/auth/verify/?token=...` | Confirmar correo. |
| Correo enviado | `/auth/email-sent/` | Confirmar envío del mensaje. |
| Listado de habitaciones | `/habitaciones/` | Navegar habitaciones activas. |
| Detalle de habitación | `/habitaciones/<pk>/` | Ver información de una habitación. |
| Búsqueda de disponibilidad | `/habitaciones/buscar/` | Buscar por fechas y capacidad. |
| Mis reservas | `/reservas/mis-reservas/` | Ver historial y estados. |
| Carrito | `/reservas/carrito/` | Revisar selección antes del checkout. |
| Checkout | `/reservas/checkout/` | Confirmar datos del cliente. |
| Pasarela HotelPay | `/reservas/hotelpay/<token>/` | Simular pago. |
| Resultado de pago | `/reservas/hotelpay/<token>/resultado/` | Mostrar aprobación o rechazo. |
| Dashboard admin | `/reportes/` | Visualizar métricas. |
| Reportes tabulares | `/reportes/reservas/`, `/reportes/clientes/`, `/reportes/habitaciones/` | Analítica operativa. |

## 6. Base de datos

### Diseño lógico

La base de datos sigue un esquema relacional normalizado alrededor de usuarios, habitaciones, reservas, pagos y tokens de verificación.

### Tablas principales

- `authapp_customuser`
- `authapp_emailverificationtoken`
- `habitaciones_tipohabitacion`
- `habitaciones_habitacion`
- `reservas_politicacancelacion`
- `reservas_reserva`
- `reservas_pago`

### Relaciones entre tablas

- `authapp_emailverificationtoken.user` -> `authapp_customuser.id`
- `habitaciones_habitacion.tipo` -> `habitaciones_tipohabitacion.id`
- `reservas_reserva.usuario` -> `authapp_customuser.id`
- `reservas_reserva.habitacion` -> `habitaciones_habitacion.id`
- `reservas_pago.reserva` -> `reservas_reserva.id`

### Llaves primarias y foráneas

- Todas las tablas usan `id` como llave primaria autoincremental `BigAutoField`.
- Las llaves foráneas usan `PROTECT`, `CASCADE` o `SET_NULL` según el dominio.
- `Reserva.codigo` y `Pago.referencia` son identificadores funcionales únicos.

### Observación sobre la base local incluida

La base `db.sqlite3` del repositorio contiene datos de ejemplo y no solo tablas vacías. En el estado actual se observan registros de usuarios, habitaciones, reservas, pagos y tokens de verificación.

## 7. Capturas del sistema

### Login
<img width="1866" height="936" alt="image" src="https://github.com/user-attachments/assets/f4c28f15-fd74-4759-ab8d-fe5e105c6ec4" />


### Registro
<img width="1866" height="917" alt="image" src="https://github.com/user-attachments/assets/86b1fc87-4086-46ce-9d74-7050e4adae0d" />


### Dashboard Administrador
<img width="1866" height="935" alt="image" src="https://github.com/user-attachments/assets/1868e819-cb03-4a0e-93d1-f7b46c90fc91" />

<img width="1862" height="930" alt="image" src="https://github.com/user-attachments/assets/c46d326f-f59d-4c02-be72-d10c8f7ed20c" />

### Gestión de habitaciones
<img width="1637" height="802" alt="image" src="https://github.com/user-attachments/assets/5070872a-8833-4ca3-8b10-b5777d1ec050" />

### Gestión de tipos de habitación
<img width="1627" height="731" alt="image" src="https://github.com/user-attachments/assets/b2eac8b8-e32e-496e-b23a-ee9bfd714319" />

### Búsqueda de disponibilidad
<img width="1631" height="617" alt="image" src="https://github.com/user-attachments/assets/8d22d17e-b2f5-443f-acaa-545d9fd341c8" />

### Carrito de reservas
<img width="1612" height="862" alt="image" src="https://github.com/user-attachments/assets/97e6c89c-2c01-4d0e-bdd0-fd0f91ab049e" />

### Checkout / HotelPay
<img width="772" height="797" alt="image" src="https://github.com/user-attachments/assets/9a2c982f-908f-4967-a916-4256858b15fa" />

### Mis reservas
<img width="1595" height="922" alt="image" src="https://github.com/user-attachments/assets/07382eb4-08c3-4c22-8fe0-22899f47032c" />

### Reportes PDF
<img width="1621" height="917" alt="image" src="https://github.com/user-attachments/assets/3c3d52e3-f7f5-46fb-ac2f-093fe55aa135" />

<img width="1087" height="236" alt="image" src="https://github.com/user-attachments/assets/febf9125-3228-4c39-b002-17afd0a078e5" />

## 8. Problemas resueltos y decisiones técnicas

### Decisiones de arquitectura

- Se implementó un usuario personalizado desde el inicio para soportar roles y verificación de correo.
- Se usó una pasarela simulada para representar un flujo real de pago sin depender de servicios externos durante el desarrollo.
- Se adoptó un carrito en sesión para simplificar la experiencia de reservar múltiples habitaciones antes del checkout.
- Se usaron reportes con PDF para cubrir necesidad operativa sin introducir un stack adicional de BI.

### Optimizaciones implementadas

- Uso de `select_related` y `prefetch_related` en consultas frecuentes.
- Borrado lógico de habitaciones con `activa=False` en vez de eliminar registros que ya tienen trazabilidad.
- Generación de códigos de reserva y referencias de pago únicas.
- Cálculo centralizado de métricas en `reportes/services.py`.

### Riesgos y problemas técnicos abordados

- Se endureció `Hotel/settings.py` para soportar variables de entorno, hosts permitidos, cache estática y configuración de seguridad para producción.
- Se corrigió el enlace de verificación de correo para que se construya con el host real de la solicitud(aun asi las nuevas configuraciones de render ya no permiten conexiones smtp en el nivel gratuito).
- Se reparó la exportación PDF de reservas y la protección de las vistas administrativas de reportes.
- La pasarela `HotelPay` sigue dependiendo de cache de proceso; en despliegues con múltiples workers debe revisarse el backend de cache.
- No existe flujo de recuperación de contraseña.
- No existe un seed automático de superusuario.

