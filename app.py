from datetime import datetime
import os
import sqlite3
from flask import Flask, redirect, render_template, request, send_from_directory, url_for

app = Flask(__name__)

UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__))
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prospectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            whatsapp TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


def buscar_archivo_flexible(nombre_buscado):
    """
    Busca un archivo en la carpeta de forma flexible, ignorando
    mayúsculas, minúsculas o ligeras variaciones en el nombre.
    """
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

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO prospectos (nombre, email, whatsapp) VALUES (?, ?, ?)",
        (nombre, email, whatsapp),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("gracias"))


@app.route("/gracias")
def gracias():
    return render_template("gracias.html")


# Ruta inteligente y robusta para el libro de Claridad
@app.route("/descargar-libro")
def descargar_libro():
    nombre_archivo = buscar_archivo_flexible("claridad_en_el_fuego.pdf")
    if not nombre_archivo:
        # Intento de respaldo por si se renombró de forma corta
        nombre_archivo = buscar_archivo_flexible("claridad.pdf")
    
    if not nombre_archivo:
        return "El archivo del libro no se encuentra disponible temporalmente en el servidor.", 404
        
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        nombre_archivo,
        as_attachment=False,
    )


# Ruta inteligente y robusta para el libro de Arte Invisible
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


# Panel de administración para ver los prospectos
@app.route("/admin")
def admin():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre, email, whatsapp, fecha FROM prospectos ORDER BY fecha DESC"
    )
    prospectos = cursor.fetchall()
    conn.close()
    return render_template("admin.html", prospectos=prospectos)


if __name__ == "__main__":
    app.run(debug=True)