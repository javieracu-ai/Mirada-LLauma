from datetime import datetime
import os
import sqlite3
from flask import Flask, redirect, render_template, request, send_from_directory, url_for

app = Flask(__name__)

UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__))
CRM_DB_PATH = os.path.join(UPLOAD_FOLDER, "database.db")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def init_db():
    conn = sqlite3.connect(CRM_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prospectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            whatsapp TEXT,
            assistant_name TEXT DEFAULT '1',
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("PRAGMA table_info(prospectos)")
    columnas = {columna[1] for columna in cursor.fetchall()}
    if "assistant_name" not in columnas:
        cursor.execute(
            "ALTER TABLE prospectos ADD COLUMN assistant_name TEXT DEFAULT '1'"
        )
    conn.commit()
    conn.close()


init_db()


def buscar_archivo_flexible(nombre_buscado):
    ruta_exacta = os.path.join(app.config["UPLOAD_FOLDER"], nombre_buscado)
    if os.path.exists(ruta_exacta):
        return nombre_buscado
        
    try:
        archivos = os.listdir(app.config["UPLOAD_FOLDER"])
        for archivo in archivos:
            if archivo.lower() == nombre_buscado.lower():
                return archivo
    except Exception:
        pass
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/guardar", methods=["POST"])
def guardar():
    nombre = request.form["nombre"]
    email = request.form["email"]
    whatsapp = request.form["whatsapp"]
    assistant_name = request.form.get("assistant_name", "1")  # Opción por defecto 1

    conn = sqlite3.connect(CRM_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO prospectos (nombre, email, whatsapp, assistant_name) VALUES (?, ?, ?, ?)",
        (nombre, email, whatsapp, assistant_name),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("gracias"))


@app.route("/gracias")
def gracias():
    return render_template("gracias.html")


@app.route("/descargar-libro")
def descargar_libro():
    nombre_archivo = buscar_archivo_flexible("claridad_en_el_fuego.pdf")
    if not nombre_archivo:
        nombre_archivo = buscar_archivo_flexible("claridad.pdf")
    
    if not nombre_archivo:
        return "El archivo del libro no se encuentra disponible temporalmente en el servidor.", 404
        
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        nombre_archivo,
        as_attachment=False,
    )


@app.route("/descargar-arte-invisible")
def descargar_arte_invisible():
    nombre_archivo = buscar_archivo_flexible("el_arte_de_lo_invisible.pdf")
    if not nombre_archivo:
        return "El archivo del libro no se encuentra disponible temporalmente en el servidor.", 404
        
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        nombre_archivo,
        as_attachment=False,
    )


# Ruta para actualizar el "Assistant's Name" directamente desde la tabla de administración
@app.route("/actualizar-assistant/<int:id>", methods=["POST"])
def actualizar_assistant(id):
    nuevo_valor = request.form.get("assistant_name")
    conn = sqlite3.connect(CRM_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE prospectos SET assistant_name = ? WHERE id = ?", (nuevo_valor, id))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))


# Panel de administración para ver los prospectos
@app.route("/admin")
def admin():
    conn = sqlite3.connect(CRM_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre, email, whatsapp, assistant_name, fecha FROM prospectos ORDER BY fecha DESC"
    )
    prospectos = cursor.fetchall()
    conn.close()
    return render_template("admin.html", prospectos=prospectos)


if __name__ == "__main__":
    app.run(debug=True)