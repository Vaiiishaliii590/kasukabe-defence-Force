from flask import Flask, render_template, request, jsonify, url_for, session, redirect
import os, sqlite3
from dotenv import load_dotenv
import google.generativeai as genai

# -------------------- APP & CONFIG --------------------
load_dotenv()
app = Flask(__name__)
app.secret_key = "supersecret"  # Required for sessions


# -------------------- DATABASE SETUP --------------------
import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()



def user_exists():
    """Check if at least one user exists in DB."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count > 0


# -------------------- GEMINI API --------------------
def _get_api_key() -> str:
    return (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or ""
    )


# -------------------- CHARACTER PROMPTS --------------------
def _character_prompt(character: str) -> str:
    characters = {
        "einstein": {
            "name": "Albert Einstein",
            "role": "Theoretical Physicist",
            "tone": "curious, reflective, accessible",
            "highlights": [
                "Special and General Relativity",
                "Photoelectric Effect (Nobel Prize, 1921)",
                "Mass–Energy Equivalence (E = mc^2)"
            ],
        },
        "newton": {
            "name": "Isaac Newton",
            "role": "Mathematician and Natural Philosopher",
            "tone": "precise, formal, insightful",
            "highlights": [
                "Laws of Motion and Universal Gravitation",
                "Infinitesimal Calculus (co-creator)",
                "Contributions to Optics"
            ],
        },
        "aryabhatta": {
            "name": "Aryabhatta",
            "role": "Mathematician and Astronomer",
            "tone": "scholarly, humble, succinct",
            "highlights": [
                "Approximation of π and use of place-value system",
                "Trigonometric functions (jya/sine, kojya/cosine)",
                "Insights on Earth's rotation"
            ],
        },
    }

    c = characters.get(character)
    if not c:
        return ""

    lines = [
        f"You are {c['name']}, a {c['role']}.",
        f"Speak in a {c['tone']} tone.",
        "Introduce yourself in 3-5 sentences to a general audience.",
        "Then briefly list 3 key contributions as bullet points.",
        "Avoid invented facts; be accurate and concise.",
        "Key highlights to touch on:"
    ]
    for h in c["highlights"]:
        lines.append(f"- {h}")
    return "\n".join(lines)


# -------------------- ROUTES --------------------

@app.route("/")
def start():
    # First-time visitor → signup page
    if not user_exists():
        return redirect(url_for("signup"))
    # Returning visitor → login page
    elif "user" not in session:
        return redirect(url_for("login"))
    # Logged in → home
    else:
        return redirect(url_for("home"))


# Signup route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            session["user"] = username
            return redirect(url_for("home"))
        except sqlite3.IntegrityError:
            return "Username already exists. Try another."
        finally:
            conn.close()
    return render_template("signup.html")


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return "Invalid username or password."

    return render_template("login.html")


# Home route → index.html (AI content)
@app.route("/home", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    intros = {}
    if request.method == "POST":
        character = (request.form.get("character") or "").lower().strip()
        prompt = _character_prompt(character)
        api_key = _get_api_key()

        if prompt and api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                resp = model.generate_content(prompt)
                intros[character] = resp.text or ""
            except Exception:
                intros[character] = "(AI generation failed. Check API key and network.)"
        else:
            intros[character] = "(Missing API key or invalid character.)"

    return render_template("index.html", username=session["user"], intros=intros)


# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# Health check
@app.route("/health")
def health():
    return {"status": "ok"}


# Error handling
@app.errorhandler(404)
def not_found(_e):
    return render_template("404.html"), 404


# -------------------- MAIN ENTRY --------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
