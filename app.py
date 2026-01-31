from flask import Flask, render_template, request, redirect
from collections import defaultdict
import sqlite3
import os

app = Flask(__name__)

# Ruta fija a la base de datos (siempre el mismo archivo)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "finanzas.db")


def crear_tabla():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


crear_tabla()


@app.route("/")
def index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movimientos")
    movimientos = cursor.fetchall()

    ingresos = 0
    gastos = 0
    gastos_por_categoria = defaultdict(float)

    for m in movimientos:
        tipo = m[1]
        categoria = m[2]
        descripcion = m[3]
        monto = float(m[4])

        if tipo == "ingreso":
            ingresos += monto
        else:
            gastos += monto
            gastos_por_categoria[categoria] += monto

    balance = ingresos - gastos
    conn.close()

    return render_template(
        "index.html",
        movimientos=movimientos,
        balance=balance,
        ingresos=ingresos,
        gastos=gastos,
        categorias=list(gastos_por_categoria.keys()),
        montos=list(gastos_por_categoria.values())
    )


@app.route("/agregar", methods=["POST"])
def agregar():
    tipo = request.form["tipo"]
    categoria = request.form["categoria"]
    descripcion = request.form["descripcion"]
    monto = float(request.form["monto"])
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO movimientos (tipo, categoria, descripcion, monto) VALUES (?, ?, ?, ?)",
        (tipo, categoria, descripcion, monto)
    )
    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
