from app import db  # Importa la instancia de SQLAlchemy inicializada en app.py
from flask_login import UserMixin

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    fecha_pedido = db.Column(db.Date, nullable=False)
    total = db.Column(db.Float, nullable=False)

    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    tamano = db.Column(db.String(50), nullable=False)
    ingredientes = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def check_password(self, password):
        return self.password == password
