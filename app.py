from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from db import get_db
from translator import translate_text
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"
CORS(app)

# ----------------- Serve Pages -----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login_page")
def login_page():
    return render_template("login.html")

@app.route("/translate_page")
def translate_page():
    if "user_id" not in session:
        return render_template("login.html", error="Login required")
    return render_template("translate.html")

# ----------------- Backend APIs -----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    phone = data.get("number")
    name = data.get("name")
    password = data.get("password")
    
    if not phone or not name or not password:
        return jsonify({"status":"error","message":"All fields required"})

    password_hash = generate_password_hash(password)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (phone_number, name, password_hash) VALUES (%s,%s,%s)",
            (phone, name, password_hash)
        )
        conn.commit()
        return jsonify({"status":"success","message":"Registration successful"})
    except:
        return jsonify({"status":"error","message":"Number already exists"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    phone = data.get("number")
    password = data.get("password")
    
    if not phone or not password:
        return jsonify({"status":"error","message":"All fields required"})
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE phone_number=%s", (phone,))
    user = cursor.fetchone()
    
    if user and check_password_hash(user["password_hash"], password):
        session["user_id"] = user["id"]
        session["name"] = user["name"]
        return jsonify({"status":"success","message":"Login successful"})
    else:
        return jsonify({"status":"error","message":"Invalid number or password"})

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status":"success","message":"Logged out"})

@app.route("/translate", methods=["POST"])
def translate():
    if "user_id" not in session:
        return jsonify({"status":"error","message":"Login required"}), 401

    data = request.json
    src = data.get("source")
    tgt = data.get("target")
    text = data.get("text")

    if not text.strip():
        return jsonify({"status":"error","message":"Enter text to translate"})

    translation = translate_text(src, tgt, text)
    
    if translation == "Translation Failed":
        return jsonify({"status":"error","message":"Translation failed, try again"})
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO translations (user_id, source_lang, target_lang, input_text, output_text) VALUES (%s,%s,%s,%s,%s)",
        (session["user_id"], src, tgt, text, translation)
    )
    conn.commit()
    
    return jsonify({"status":"success","translation": translation})

if __name__ == "__main__":
    app.run(debug=True)
