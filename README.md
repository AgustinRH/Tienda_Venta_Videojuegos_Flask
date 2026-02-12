# Proyecto Flask - Tienda de Articulos

Aplicacion web en Flask para mostrar articulos por categorias, con registro/login, perfil de usuario y un panel de administracion para gestionar categorias y articulos. Usa SQLite y Flask-Login para autenticacion.

## Caracteristicas

- Catalogo de articulos con filtros por categoria.
- Registro, login, logout y cambio de contrasena.
- Roles: usuario normal y administrador.
- CRUD de categorias (solo admin).
- CRUD de articulos con subida de imagen (solo admin).
- Formularios con Flask-WTF.
- Base de datos SQLite con SQLAlchemy.

## Requisitos

- Python 3.10+ (recomendado)
- Paquetes en requirements.txt

## Instalacion

1) Crea y activa un entorno virtual.
2) Instala dependencias:

```bash
pip install -r requirements.txt
```

## Configuracion

La configuracion esta en [aplicacion/config.py](aplicacion/config.py):

- `SECRET_KEY`: clave para sesiones y formularios.
- `SQLALCHEMY_DATABASE_URI`: base SQLite en `dbase.db` dentro del proyecto.
- `DEBUG`: modo debug.

Recomendacion: cambiar `SECRET_KEY` antes de poner en produccion.

## Inicializar la base de datos

El archivo [manage.py](manage.py) define comandos de Flask CLI:

```bash
flask create_tables
```

Crea tablas y agrega la categoria "Todos".

Para cargar datos de ejemplo:

```bash
flask add_data_tables
```

Para crear un administrador:

```bash
flask create_admin
```

Para borrar todas las tablas (elimina datos):

```bash
flask drop_tables
```

## Ejecutar la aplicacion

```bash
python aplicacion/app.py
```

La app quedara disponible en `http://127.0.0.1:5000/`.

## Uso

- Pagina principal: lista de articulos y filtros por categoria.
- Registro/login: rutas `/registro` y `/login`.
- Perfil de usuario: `/perfil/<username>` y cambio de contrasena en `/changepassword/<username>`.
- Admin:
  - Categorias: `/categorias`, `/categorias/new`, `/categorias/edit/<id>`, `/categorias/delete/<id>`.
  - Articulos: `/articulos/new`, `/articulos/edit/<id>`, `/articulos/delete/<id>`.

## Estructura del proyecto

```
.
├── aplicacion/
│   ├── app.py            # Rutas y configuracion de la app
│   ├── config.py         # Configuracion
│   ├── forms.py          # Formularios Flask-WTF
│   ├── login.py          # Helpers de sesion (no usados por Flask-Login)
│   ├── models.py         # Modelos SQLAlchemy
│   ├── static/
│   │   └── img/           # Imagenes subidas
│   └── templates/         # Plantillas HTML
├── manage.py             # Comandos CLI
└── requirements.txt      # Dependencias
```

## Modelos principales

- `Categorias`: nombre y relacion con articulos.
- `Articulos`: nombre, precio, IVA, descripcion, imagen, stock, categoria.
- `Usuarios`: username, password hash, nombre, email, admin.

## Notas

- La subida de imagenes guarda archivos en `aplicacion/static/img/`.
- El carrito esta planteado con un formulario basico y una ruta de ejemplo (`/carrito/add`).

## Licencia

Este proyecto no especifica licencia.
