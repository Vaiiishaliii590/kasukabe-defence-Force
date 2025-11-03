from flask import Flask, render_template, request, jsonify, flash, url_for, session, flash, redirect
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
app = Flask(__name__)
def _get_api_key() -> str:
    # Support both common env var names
    return (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or ""
    )

users = {}

@app.route("/", methods=["GET", "POST"])
def index():
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
                text = resp.text or ""
                intros[character] = text
            except Exception as _e:
                intros[character] = "(AI generation failed. Check API key and network.)"
        elif not api_key:
            intros[character] = "(Missing GEMINI_API_KEY/GOOGLE_API_KEY. Set it and retry.)"
    return render_template("index.html", intros=intros)


@app.route("/health")
def health():
    return {"status": "ok"}


@app.errorhandler(404)
def not_found(_e):
    return render_template("404.html"), 404


def _character_prompt(character: str) -> str:
    characters = {
        "einstein": {
            "name": "Albert Einstein",
            "role": "Theoretical Physicist",
            "tone": "curious, reflective, accessible",
            "highlights": [
                "Special and General Relativity",
                "Photoelectric Effect (Nobel Prize, 1921)",
                "Mass–Energy Equivalence (E = mc^2)",
            ],
        },
        "newton": {
            "name": "Isaac Newton",
            "role": "Mathematician and Natural Philosopher",
            "tone": "precise, formal, insightful",
            "highlights": [
                "Laws of Motion and Universal Gravitation",
                "Infinitesimal Calculus (co-creator)",
                "Contributions to Optics",
            ],
        },
        "aryabhatta": {
            "name": "Aryabhatta",
            "role": "Mathematician and Astronomer",
            "tone": "scholarly, humble, succinct",
            "highlights": [
                "Approximation of pi and place-value usage",
                "Trigonometric functions (jya/sine, kojya/cosine)",
                "Insights on Earth's rotation",
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
    ]
    lines.append("Key highlights to touch on:")
    for h in c["highlights"]:
        lines.append(f"- {h}")
    return "\n".join(lines)


@app.route("/api/interview")
def api_interview():
    api_key = _get_api_key()
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY or GOOGLE_API_KEY not configured"}), 500

    character = request.args.get("character", "").lower().strip()
    prompt = _character_prompt(character)
    if not prompt:
        return jsonify({"error": "unknown character"}), 400

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        resp = model.generate_content(prompt)
        text = resp.text or ""
        return jsonify({"character": character, "text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username] == password:
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials, please try again.", "error")
    
    return '''
        <form method="POST">
            <h2>Login</h2>
            <input type="text" name="username" placeholder="Username" required><br><br>
            <input type="password" name="password" placeholder="Password" required><br><br>
            <button type="submit">Login</button>
        </form>
        <a href="/signup">Don't have an account? Signup</a>
    '''

@app.route("/home")
def home():
    if "user" in session:
        return f'''
            <h1>Welcome, {session["user"]}!</h1>
            <a href="/logout">Logout</a>
        '''
    else:
        flash("Please login first.", "error")
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
