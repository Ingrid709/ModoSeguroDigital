from flask import Flask, request, redirect, render_template, session
import sqlite3

app = Flask(__name__)
app.secret_key = "ciberseguridad2024"

WIX_URL = "https://modosegurodigital.wixsite.com/modosegurodigital"

def get_db():
    db = sqlite3.connect("users.db")
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    try:
        db.execute("INSERT INTO users (username, password) VALUES (?,?)", ("admin","admin123"))
    except:
        pass
    db.commit()
    db.close()

@app.route("/")
def index():
    return redirect("/login")

@app.route("/register", methods=["GET","POST"])
def register():
    error = success = None
    if request.method == "POST":
        u = request.form["username"].strip()
        p = request.form["password"].strip()
        try:
            db = get_db()
            db.execute("INSERT INTO users (username, password) VALUES (?,?)", (u, p))
            db.commit()
            db.close()
            success = f"Usuario '{u}' registrado correctamente."
        except sqlite3.IntegrityError:
            error = "Ese usuario ya existe."
    return render_template("register.html", error=error, success=success)

@app.route("/login", methods=["GET","POST"])
def login():
    error = query = None
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        query = f"SELECT * FROM users WHERE username = '{u}' AND password = '{p}'"

        try:
            db = sqlite3.connect("users.db")
            db.row_factory = sqlite3.Row
            # executescript ejecuta múltiples comandos SQL
            db.executescript(query)
            db.commit()
            try:
                user = db.execute(f"SELECT * FROM users WHERE username = '{u}' AND password = '{p}'").fetchone()
            except:
                user = None
            db.close()
            if user:
                return redirect(WIX_URL)
            else:
                error = "Usuario o contraseña incorrectos."
        except Exception as e:
            error = f"Error SQL: {e}"

    return render_template("login.html", error=error, query=query)

@app.route("/login-seguro", methods=["GET","POST"])
def login_seguro():
    error = query = None
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (u, p)).fetchone()
        db.close()
        query = f"SELECT * FROM users WHERE username = ? AND password = ?   →   valores: ('{u}', '{p}')"
        if user:
            return redirect(WIX_URL)
        else:
            error = "Usuario o contraseña incorrectos. El SQL Injection no funciona aquí."

    return render_template("login_seguro.html", error=error, query=query)

if __name__ == "__main__":
    init_db()
    print("\n  http://127.0.0.1:5000")
    print("   /register     → Registro")
    print("   /login        → Login VULNERABLE")
    print("   /login-seguro → Login SEGURO\n")
    app.run(debug=True)
