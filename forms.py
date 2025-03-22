from wtforms import Form, StringField, IntegerField, SelectMultipleField, SubmitField, RadioField, PasswordField, BooleanField
from wtforms import validators
from wtforms.validators import DataRequired, Length, Email



class PedidoForm(Form):
    nombre = StringField('Nombre Completo', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.Length(min=4, max=50, message='Debe tener entre 4 y 50 caracteres')
    ])
    
    direccion = StringField('Dirección', [
        validators.DataRequired(message='La dirección es requerida'),
        validators.Length(min=5, max=100, message='Debe tener entre 5 y 100 caracteres')
    ])
    
    telefono = StringField('Teléfono', [
        validators.DataRequired(message='El teléfono es requerido'),
        validators.Regexp(r'^\d{10}$', message='El teléfono debe tener 10 dígitos')
    ])
    
    tamano = RadioField('Tamaño de la Pizza', choices=[
        ('Chica', 'Chica - $40'),
        ('Mediana', 'Mediana - $80'),
        ('Grande', 'Grande - $120')
    ], default='Chica', validators=[validators.DataRequired()])
    
    ingredientes = SelectMultipleField("Ingredientes", choices=[
    ("Jamón", "Jamón"),
    ("Piña", "Piña"),
    ("Champiñones", "Champiñones")
    ]   , validators=[validators.DataRequired()])
    
    cantidad = IntegerField('Número de Pizzas', [
        validators.DataRequired(),
        validators.NumberRange(min=1, message='Debe pedir al menos una pizza')
    ], default=1)  

    agregar = SubmitField('Agregar Pizza')
    quitar = SubmitField('Quitar Pizza')
    terminar = SubmitField('Finalizar Pedido')


class ReporteForm(Form):
    filtro = RadioField('Filtrar por:', choices=[('dia', 'Día'), ('mes', 'Mes')], default='dia')
    fecha = StringField('Fecha (YYYY-MM o YYYY-MM-DD)', validators=[validators.DataRequired()])
    buscar = SubmitField('Buscar')

class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
