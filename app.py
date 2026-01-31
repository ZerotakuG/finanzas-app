from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
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
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM movimientos")
    movimientos = c.fetchall()

    # Calcular balance
    balance = sum(m[3] if m[1] == "ingreso" else -m[3] for m in movimientos)

    # Agrupar gastos por descripción
    gastos = {}
    for m in movimientos:
        if m[1] == "gasto":
            gastos[m[2]] = gastos.get(m[2], 0) + m[3]

    conn.close()

    return render_template("index.html",
                           movimientos=movimientos,
                           balance=balance,
                           gastos_labels=list(gastos.keys()),
                           gastos_data=list(gastos.values()))

@app.route("/agregar", methods=["POST"])
def agregar():
    tipo = request.form["tipo"]
    descripcion = request.form["descripcion"]
    monto = float(request.form["monto"])

    conn = sqlite3.connect("database.db")
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
