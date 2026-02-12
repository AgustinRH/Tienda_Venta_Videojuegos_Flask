from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileField

class formCarrito(FlaskForm):
    id = HiddenField() # Almacena el ID del artículo de forma invisible
    cantidad = IntegerField('Cantidad', default=1, 
                            validators=[NumberRange(min=1, message="Debe ser un número positivo"), 
                                        DataRequired("Tienes que introducir el dato")])
    submit = SubmitField('Aceptar')

class formArticulo(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired("Tienes que poner un nombre")])
    precio = DecimalField('Precio', default=0, validators=[DataRequired("Tienes que poner un precio")])
    iva = IntegerField('IVA', default=21, validators=[DataRequired("Tienes que poner un IVA")])
    descripcion = TextAreaField('Descripción:')
    photo = FileField('Selecciona imagen:')
    stock = IntegerField('Stock:', default=1, validators=[DataRequired("Tienes que poner una cantidad de stock")])
    CategoriaId = SelectField('Categoría:', coerce=int)
    submit = SubmitField('Enviar')
    
class formCategoria(FlaskForm):
    nombre = StringField('Nombre:', validators=[DataRequired("Tienes que poner un nombre")])
    submit = SubmitField('Enviar')
    
class formSINO(FlaskForm):
    si = SubmitField('Si')
    no = SubmitField('No')

class LoginForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired("Tienes que poner un nombre de usuario")])
    password = PasswordField('Password', validators=[DataRequired("Tienes que poner una contraseña")])
    submit = SubmitField('Entrar')
    
class formUsuario(FlaskForm):
    username = StringField('Login', validators=[DataRequired("Tienes que poner un nombre de usuario")])
    password = PasswordField('Password', validators=[DataRequired("Tienes que poner una contraseña")])
    nombre = StringField('Nombre completo', validators=[DataRequired("Tienes que poner un nombre completo")])
    email = StringField('Email', validators=[DataRequired("Tienes que poner un email")])
    # Nuevo campo opcional
    admin_token = PasswordField('Código de Administrador (Opcional)') 
    submit = SubmitField('Registrar')
    
class formChangePassword(FlaskForm):
    # Campo para la contraseña que tiene ahora
    antigua_password = PasswordField('Contraseña Actual', validators=[DataRequired()])
    # Campo para la nueva
    password = PasswordField('Nueva Contraseña', validators=[DataRequired()])
    submit = SubmitField('Cambiar Contraseña')