from flask import render_template, request, redirect, flash, url_for, session
from app import app, db
from models import Cliente, Pedido, User
from forms import PedidoForm, LoginForm
from flask_login import current_user, login_user, logout_user, login_required
import datetime
import os

ARCHIVO_TEMPORAL = "pedidos.txt"

PRECIOS_PIZZA = {"Chica": 40, "Mediana": 80, "Grande": 120}
PRECIOS_INGREDIENTES = {"Jamón": 10, "Piña": 10, "Champiñones": 10}

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = PedidoForm(request.form)
    pedidos = []
    filtro = request.form.get("filtro", "dia")  
    fecha_input = request.form.get("fecha", datetime.date.today().strftime("%Y-%m-%d"))
    ventas_filtradas = []
    total_ventas_filtradas = 0

    # Leer los pedidos desde el archivo temporal
    if os.path.exists(ARCHIVO_TEMPORAL):
        with open(ARCHIVO_TEMPORAL, "r") as f:
            for linea in f:
                datos = linea.strip().split(" - ")
                if len(datos) == 4:
                    pedidos.append(datos)

    if request.method == "POST":
        session["nombre"] = form.nombre.data
        session["direccion"] = form.direccion.data
        session["telefono"] = form.telefono.data

        if "agregar" in request.form:
            tamano = form.tamano.data
            cantidad = form.cantidad.data
            ingredientes_lista = form.ingredientes.data or []
            if not tamano or tamano not in PRECIOS_PIZZA:
                flash("Debe seleccionar un tamaño de pizza válido.", "danger")
                return redirect(url_for('index'))
            if not cantidad or cantidad < 1:
                flash("Debe ingresar una cantidad válida mayor o igual a 1.", "danger")
                return redirect(url_for('index'))
            if not ingredientes_lista:
                flash("Debe seleccionar al menos un ingrediente.", "danger")
                return redirect(url_for('index'))

            ingredientes = ", ".join(ingredientes_lista)
            precio_unitario = PRECIOS_PIZZA[tamano]
            subtotal = (cantidad * precio_unitario) + sum(
                PRECIOS_INGREDIENTES.get(i.strip(), 0) * cantidad for i in ingredientes_lista
            )

            with open(ARCHIVO_TEMPORAL, "a") as f:
                f.write(f"{tamano} - {cantidad} - {ingredientes} - {subtotal}\n")

            flash(f"Pizza agregada: {cantidad} x {tamano} con {ingredientes} (${subtotal})", "success")
            return redirect(url_for('index'))

        elif "quitar" in request.form:
            if pedidos:
                pedidos.pop()
                with open(ARCHIVO_TEMPORAL, "w") as f:
                    for p in pedidos:
                        f.write(" - ".join(p) + "\n")
                flash("Última pizza eliminada.", "warning")
            return redirect(url_for('index'))

        elif "eliminar_pedido" in request.form:
            index_eliminar = int(request.form.get("index_eliminar"))
            
            if 0 <= index_eliminar < len(pedidos):
                pedidos.pop(index_eliminar)
                
                with open(ARCHIVO_TEMPORAL, "w") as f:
                    for p in pedidos:
                        f.write(" - ".join(p) + "\n")

                flash("Pedido eliminado correctamente.", "warning")
            return redirect(url_for('index'))

        elif "terminar" in request.form:
            total = sum(float(p[3]) for p in pedidos if len(p) == 4)

            if not (form.nombre.data and form.direccion.data and form.telefono.data):
                flash("Todos los datos del cliente (nombre, dirección, teléfono) son obligatorios para completar el pedido.", "danger")
                return redirect(url_for('index'))

            cliente = Cliente(
                nombre=form.nombre.data,
                direccion=form.direccion.data,
                telefono=form.telefono.data,
                fecha_pedido=datetime.date.today(),
                total=total
            )
            db.session.add(cliente)
            db.session.commit()

            for p in pedidos:
                pedido = Pedido(
                    cliente_id=cliente.id,
                    tamano=p[0],
                    cantidad=int(p[1]),
                    ingredientes=p[2],
                    subtotal=float(p[3])
                )
                db.session.add(pedido)

            db.session.commit()

            os.remove(ARCHIVO_TEMPORAL)
            session.pop("nombre", None)
            session.pop("direccion", None)
            session.pop("telefono", None)

            flash(f"Pedido completado. Total a pagar: ${total:.2f}", "success")
            return redirect(url_for('index'))

        elif "buscar" in request.form:
            try:
                if filtro == "dia":
                    fecha_buscada = datetime.datetime.strptime(fecha_input, "%Y-%m-%d").date()
                    ventas_filtradas = Cliente.query.filter_by(fecha_pedido=fecha_buscada).all()
                elif filtro == "mes":
                    año, mes = map(int, fecha_input.split("-"))
                    ventas_filtradas = Cliente.query.filter(
                        db.extract("year", Cliente.fecha_pedido) == año,
                        db.extract("month", Cliente.fecha_pedido) == mes
                    ).all()

                total_ventas_filtradas = sum(cliente.total for cliente in ventas_filtradas)
            except ValueError:
                flash("Formato de fecha incorrecto. Usa YYYY-MM-DD para día o YYYY-MM para mes.", "danger")
                return redirect(url_for('index'))

    form.nombre.data = session.get("nombre", "")
    form.direccion.data = session.get("direccion", "")
    form.telefono.data = session.get("telefono", "")

    fecha_hoy = datetime.date.today()
    ventas_hoy = Cliente.query.filter_by(fecha_pedido=fecha_hoy).all()
    total_ventas_dia = sum(cliente.total for cliente in ventas_hoy)

    return render_template(
        "index.html",
        form=form,
        pedidos=pedidos,
        ventas_hoy=ventas_hoy,
        total_ventas_dia=total_ventas_dia,
        ventas_filtradas=ventas_filtradas,
        total_ventas_filtradas=total_ventas_filtradas,
        filtro=filtro,
        fecha_input=fecha_input
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))

        flash('Correo o contraseña incorrectos', 'danger')
        return render_template("login.html", form=form)  # Renderizar de inmediato si hay error

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
