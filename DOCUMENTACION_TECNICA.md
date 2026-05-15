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

El proyecto sigue una arquitectura monolítica Django clásica, organizada por apps funcionales:

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
[Agregar captura aquí]

### Registro
[Agregar captura aquí]

### Dashboard Administrador
[Agregar captura aquí]

### Gestión de habitaciones
[Agregar captura aquí]

### Gestión de tipos de habitación
[Agregar captura aquí]

### Búsqueda de disponibilidad
[Agregar captura aquí]

### Carrito de reservas
[Agregar captura aquí]

### Checkout / HotelPay
[Agregar captura aquí]

### Mis reservas
[Agregar captura aquí]

### Reportes PDF
[Agregar captura aquí]

## 8. Problemas resueltos y decisiones técnicas

### Decisiones de arquitectura

- Se eligió una arquitectura monolítica Django porque el alcance funcional es claro y el tiempo de desarrollo se beneficia de mantener frontend y backend en el mismo proyecto.
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
- Se corrigió el enlace de verificación de correo para que se construya con el host real de la solicitud.
- Se reparó la exportación PDF de reservas y la protección de las vistas administrativas de reportes.
- La pasarela `HotelPay` sigue dependiendo de cache de proceso; en despliegues con múltiples workers debe revisarse el backend de cache.
- No existe flujo de recuperación de contraseña.
- No existe un seed automático de superusuario.
