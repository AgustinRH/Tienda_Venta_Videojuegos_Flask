import os
from flask import Flask, render_template, redirect, url_for, request, abort
from flask_bootstrap import Bootstrap5
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from aplicacion import config
from aplicacion.models import db, Articulos, Categorias, Usuarios
from aplicacion.forms import (LoginForm, formArticulo, formCategoria, 
                              formChangePassword, formSINO, formUsuario, formCarrito)

app = Flask(__name__)
app.config.from_object(config)

# Inicialización de extensiones
bootstrap = Bootstrap5(app)
db.init_app(app)

# --- Gestión Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))

# Context Processor para facilitar el uso en plantillas
@app.context_processor
def inject_permissions():
    return dict(
        is_login=current_user.is_authenticated,
        is_admin=getattr(current_user, 'admin', False)
    )

# --- RUTAS PÚBLICAS ---

@app.route('/')
@app.route('/categoria/<int:id>')
def inicio(id=0):
    categorias = Categorias.query.all()
    if id == 0:
        articulos = Articulos.query.all()
        categoria = None
    else:
        categoria = Categorias.query.get(id)
        if categoria is None: abort(404)
        articulos = Articulos.query.filter_by(CategoriaId=id).all()
    
    # Instanciamos el formulario para pasarlo a la plantilla
    form = formCarrito() 
    
    return render_template('inicio.html', articulos=articulos, 
                           categorias=categorias, categoria=categoria, form=form)

@app.route('/categorias/edit/<int:id>', methods=["GET", "POST"])
@login_required
def categorias_edit(id):
    if not current_user.admin: abort(403)
    
    cat = Categorias.query.get_or_404(id)
    form = formCategoria(obj=cat) # Cargamos el nombre actual en el form
    
    if form.validate_on_submit():
        cat.nombre = form.nombre.data
        db.session.commit()
        return redirect(url_for("categorias_lista"))
        
    return render_template("categorias_new.html", form=form)

@app.route('/categorias/delete/<int:id>', methods=["GET", "POST"])
@login_required
def categorias_delete(id):
    if not current_user.admin: abort(403)
    
    cat = Categorias.query.get_or_404(id)
    # Verificamos si tiene artículos antes de borrar para evitar errores de integridad
    if Articulos.query.filter_by(CategoriaId=id).first():
        # Aquí podrías mandar un flash message diciendo que no se puede borrar
        return redirect(url_for("categorias_lista"))
        
    form = formSINO()
    if form.validate_on_submit():
        if form.si.data:
            db.session.delete(cat)
            db.session.commit()
        return redirect(url_for("categorias_lista"))
        
    return render_template("categorias_delete.html", form=form, cat=cat)

# --- AUTENTICACIÓN Y REGISTRO ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuarios.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('inicio'))
        form.username.errors.append("Usuario o contraseña incorrectos.")
    return render_template('login.html', form=form)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    # Refactorizado: Solo permite registro si no hay sesión iniciada
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    form = formUsuario()
    if form.validate_on_submit():
        if Usuarios.query.filter_by(username=form.username.data).first():
            form.username.errors.append("El nombre de usuario ya existe.")
            return render_template('usuarios_new.html', form=form)
        
        user = Usuarios()
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        login_user(user) # Auto-login tras registro
        return redirect(url_for('inicio'))
    return render_template('usuarios_new.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('inicio'))

# --- GESTIÓN DE PERFIL ---

@app.route('/perfil/<username>', methods=["GET", "POST"])
@login_required
def perfil(username):
    user = Usuarios.query.filter_by(username=username).first()
    if user is None: 
        abort(404)
    
    # IMPORTANTE: Cambiamos el formulario al de contraseña
    form = formChangePassword() 
    
    return render_template("perfil.html", usuario=user, form=form)

@app.route('/changepassword/<username>', methods=["GET", "POST"])
@login_required
def changepassword(username):
    user = Usuarios.query.filter_by(username=username).first()
    # ... validaciones de seguridad ...

    form = formChangePassword() # <--- ASEGÚRATE DE USAR ESTE
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        return redirect(url_for("perfil", username=user.username))
    
    return render_template("changepassword.html", form=form, usuario=user)

# --- RUTAS DE ADMINISTRACIÓN (SOLO ADMIN) ---

@app.route('/articulos/new', methods=["GET", "POST"])
@login_required
def articulos_new():
    if not current_user.admin: abort(403) # O 404 para ocultar la existencia
    
    form = formArticulo()
    form.CategoriaId.choices = [(c.id, c.nombre) for c in Categorias.query.all()]
    
    if form.validate_on_submit():
        art = Articulos()
        form.populate_obj(art)
        art.precio = round(float(form.precio.data), 2)
        
        # Gestión de imagen
        if form.photo.data:
            f = form.photo.data
            nombre_fichero = secure_filename(f.filename)
            f.save(os.path.join(app.root_path, 'static', 'img', nombre_fichero))
            art.image = nombre_fichero
            
        db.session.add(art)
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("articulos_new.html", form=form)

@app.route('/categorias', methods=["GET"])
@login_required
def categorias_lista():
    if not current_user.admin: abort(403)
    categorias = Categorias.query.all()
    return render_template('categorias.html', categorias=categorias)

@app.route('/categorias/new', methods=["GET", "POST"])
@login_required
def categorias_new():
    if not current_user.admin: abort(403)
    form = formCategoria()
    if form.validate_on_submit():
        cat = Categorias(nombre=form.nombre.data)
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for("categorias_lista"))
    return render_template("categorias_new.html", form=form)

# --- EDICIÓN Y BORRADO DE ARTÍCULOS ---

@app.route('/articulos/edit/<int:id>', methods=["GET", "POST"])
@login_required
def articulos_edit(id):
    if not current_user.admin: abort(403)
    
    art = Articulos.query.get_or_404(id)
    # Pasamos el objeto art al formulario para que se rellenen los campos automáticamente
    form = formArticulo(obj=art)
    form.CategoriaId.choices = [(c.id, c.nombre) for c in Categorias.query.all()]
    
    if form.validate_on_submit():
        form.populate_obj(art)
        
        # Gestión de nueva imagen si se sube una
        if form.photo.data:
            f = form.photo.data
            nombre_fichero = secure_filename(f.filename)
            f.save(os.path.join(app.root_path, 'static', 'img', nombre_fichero))
            art.image = nombre_fichero
        
        # Aseguramos el redondeo a 2 decimales antes de guardar
        art.precio = round(float(art.precio), 2)
        
        db.session.commit()
        return redirect(url_for("inicio"))
        
    return render_template("articulos_new.html", form=form)

@app.route('/articulos/delete/<int:id>', methods=["GET", "POST"])
@login_required
def articulos_delete(id):
    if not current_user.admin: abort(403)
    
    art = Articulos.query.get_or_404(id)
    form = formSINO() # Formulario de confirmación Sí/No
    
    if form.validate_on_submit():
        if form.si.data:
            # Borrar imagen del servidor si no es la por defecto
            if art.image:
                try:
                    os.remove(os.path.join(app.root_path, 'static', 'img', art.image))
                except:
                    pass
            db.session.delete(art)
            db.session.commit()
        return redirect(url_for("inicio"))
        
    return render_template("articulos_delete.html", form=form, art=art)

# --- GESTIÓN DEL CARRITO ---

@app.route('/carrito/add', methods=["POST"])
@login_required
def carrito_add():
    form = formCarrito()
    if form.validate_on_submit():
        # Aquí obtienes los datos del formulario
        id_articulo = request.form.get('id')
        cantidad = form.cantidad.data
        
        # Lógica para guardar en sesión o base de datos
        # Por ahora, un print para debuguear:
        print(f"Añadiendo al carrito: Articulo {id_articulo}, Cantidad {cantidad}")
        
        # Redirigir a donde prefieras (a la lista de artículos, por ejemplo)
        return redirect(url_for('inicio'))
    
    return redirect(url_for('inicio'))

# --- MANEJO DE ERRORES ---

@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html", error="Página no encontrada"), 404

@app.errorhandler(403)
def access_denied(error):
    return render_template("error.html", error="No tienes permisos para acceder aquí"), 403

if __name__ == '__main__':
    app.run(debug=True)