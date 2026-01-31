from flask import Flask, render_template, request, redirect
from collections import defaultdict
import sqlite3


app = Flask(__name__)
def crear_tabla():
    conn = sqlite3.connect("finanzas.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()
crear_tabla()

def init_db():
    conn = sqlite3.connect("finanzas.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS movimientos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT,
                    descripcion TEXT,
                    monto REAL
                )''')
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = sqlite3.connect("finanzas.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movimientos")
    movimientos = cursor.fetchall()

    ingresos = 0
    gastos = 0
    gastos_por_categoria = defaultdict(float)

    for m in movimientos:
        tipo = m[1]
        descripcion = m[2]
        monto = float(m[3])

        if tipo == "ingreso":
            ingresos += monto
        else:
            gastos += monto
            gastos_por_categoria[descripcion] += monto

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
    descripcion = request.form["descripcion"]
    monto = float(request.form["monto"])

    conn = sqlite3.connect("finanzas.db")
    c = conn.cursor()
    c.execute("INSERT INTO movimientos (tipo, descripcion, monto) VALUES (?, ?, ?)",
              (tipo, descripcion, monto))
    conn.commit()
    conn.close()

    return redirect("/")

import os

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
