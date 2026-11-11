# Herramientas en Común

Aplicación Django para administrar el inventario compartido y solicitudes de préstamo de la Junta de Vecinos Villa Los Aromos. Los encargados gestionan herramientas y préstamos; los socios pueden armar solicitudes de hasta tres herramientas.

## Requisitos

- Python 3.12 o posterior.
- SQLite para desarrollo local o PostgreSQL para la configuración de entrega.

## Instalación local (Windows PowerShell)

Desde la carpeta del proyecto:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Para ejecutar con SQLite, cambia `DB_ENGINE=sqlite` en `.env`. Para PostgreSQL, crea una base de datos llamada `herramientas_db`, configura `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT`, y deja `DB_ENGINE=postgresql`.

Los comandos Django se ejecutan desde `herramientas_comun`:

```powershell
cd herramientas_comun
..\venv\Scripts\python.exe manage.py migrate
..\venv\Scripts\python.exe manage.py loaddata herramientas_iniciales
..\venv\Scripts\python.exe manage.py crear_usuarios_demo --password "CambiaEstaClave123!"
..\venv\Scripts\python.exe manage.py runserver
```

El fixture contiene tres categorías y quince herramientas. El comando de usuarios de prueba crea `admin` (superusuario), `encargado` (con `is_staff`) y `socio` (cuenta regular), todos con la contraseña que se entrega como argumento. Úsalo solo en desarrollo y reemplaza la contraseña por una propia. En producción, crea cuentas y contraseñas individuales.

Abre <http://127.0.0.1:8000/>. El usuario y contraseña de prueba son `admin`, `encargado` y `socio`, con la contraseña elegida al ejecutar `crear_usuarios_demo`. La sesión vence a los 30 minutos.

## Rutas principales

- `/login/`: inicio de sesión.
- `/catalogo/`: catálogo y armado de solicitud.
- `/mis-prestamos/`: préstamos del socio autenticado.
- `/herramientas/`, `/categorias/` y `/prestamos/`: gestión exclusiva del encargado.
- `/admin/`: administración de Django.
