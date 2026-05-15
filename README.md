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
