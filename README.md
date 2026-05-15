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

## Riesgos conocidos

- La configuración de producción necesita endurecimiento de seguridad.
- La pasarela HotelPay usa cache temporal y debe validarse según el backend de cache del despliegue.
- No existe recuperación de contraseña.
- No hay API REST pública.
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
