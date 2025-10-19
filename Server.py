from flask import Flask, request, jsonify, g, send_file
from flask_cors import CORS
import sqlite3
import bcrypt
from io import BytesIO
from pathlib import Path
import sys

# ensure project root is on path so we can import GenerateBarcode.py
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from GenerateBarcode import GenBarcode  # noqa: E402

DB_PATH = str(Path(__file__).resolve().parents[1] / "users.db")

app = Flask(__name__)
CORS(app, supports_credentials=True)


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        DOB TEXT,
        GENDER_L TEXT,
        TRN TEXT UNIQUE,
        DOC_ID TEXT UNIQUE,
        STAFF_ID TEXT UNIQUE
    )
    """
    )
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, stored_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))


@app.before_first_request
def before_first():
    init_db()


@app.route("/register", methods=["POST"])
def register_user():
    data = request.get_json() or {}
    username = data.get("username")
    DOB = data.get("DOB")
    Gender_L = data.get("GENDER_L")
    email = data.get("email")
    password = data.get("password")
    TRN = data.get("TRN")

    if not all([username, email, password, TRN, DOB, Gender_L]):
        return jsonify({"error": "Missing information"}), 400

    db = get_db()
    cur = db.cursor()
    try:
        hashed = hash_password(password)
        cur.execute(
            "INSERT INTO users (username, email, password, DOB, GENDER_L, TRN) VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, hashed, DOB, Gender_L, TRN),
        )
        db.commit()
        return jsonify({"message": "User registered successfully", "id": cur.lastrowid}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"error": "Duplicate field or user exists", "details": str(e)}), 409


@app.route("/register/doc", methods=["POST"])
def register_doc():
    data = request.get_json() or {}
    username = data.get("username")
    DOB = data.get("DOB")
    Gender_L = data.get("GENDER_L")
    email = data.get("email")
    DOC_ID = data.get("DOC_ID")
    password = data.get("password")
    TRN = data.get("TRN")

    if not all([username, email, password, TRN, DOB, Gender_L, DOC_ID]):
        return jsonify({"error": "Missing information"}), 400

    db = get_db()
    cur = db.cursor()
    try:
        hashed = hash_password(password)
        cur.execute(
            "INSERT INTO users (username, email, password, DOB, GENDER_L, TRN, DOC_ID) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, email, hashed, DOB, Gender_L, TRN, DOC_ID),
        )
        db.commit()
        return jsonify({"message": "Doctor registered successfully", "id": cur.lastrowid}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"error": "Duplicate field or user exists", "details": str(e)}), 409


@app.route("/register/staff", methods=["POST"])
def register_staff():
    data = request.get_json() or {}
    username = data.get("username")
    DOB = data.get("DOB")
    Gender_L = data.get("GENDER_L")
    email = data.get("email")
    STAFF_ID = data.get("STAFF_ID")
    password = data.get("password")
    TRN = data.get("TRN")

    if not all([username, email, password, TRN, DOB, Gender_L, STAFF_ID]):
        return jsonify({"error": "Missing information"}), 400

    db = get_db()
    cur = db.cursor()
    try:
        hashed = hash_password(password)
        cur.execute(
            "INSERT INTO users (username, email, password, DOB, GENDER_L, TRN, STAFF_ID) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, email, hashed, DOB, Gender_L, TRN, STAFF_ID),
        )
        db.commit()
        return jsonify({"message": "Staff registered successfully", "id": cur.lastrowid}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"error": "Duplicate field or user exists", "details": str(e)}), 409


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing info"}), 400

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, password FROM users WHERE username=?", (username,))
    user = cur.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if verify_password(password, user["password"]):
        # For frontend, return minimal user info (no password)
        return jsonify({"message": "Login successful", "id": user["id"], "username": username}), 200
    else:
        return jsonify({"error": "Incorrect password"}), 401


# Barcode endpoint for frontend: returns PNG image bytes
@app.route("/barcode/<nhf>", methods=["GET"])
def barcode(nhf):
    try:
        png_bytes = GenBarcode(nhf)
        return send_file(BytesIO(png_bytes), mimetype="image/png", download_name=f"{nhf}.png", as_attachment=False)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to generate barcode", "details": str(e)}), 500


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
