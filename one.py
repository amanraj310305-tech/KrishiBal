from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ---------- Database ----------
def init_db():
    conn = sqlite3.connect("forum.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            text TEXT NOT NULL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("forum.html")

@app.route("/messages", methods=["GET"])
def get_messages():
    conn = sqlite3.connect("forum.db")
    c = conn.cursor()
    c.execute("SELECT id, parent_id, text, timestamp FROM messages ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()

    messages = [
        {"id": r[0], "parent_id": r[1], "text": r[2], "timestamp": r[3]}
        for r in rows
    ]
    return jsonify(messages)

@app.route("/messages", methods=["POST"])
def post_message():
    data = request.json
    text = data.get("text")
    parent_id = data.get("parent_id")

    if not text:
        return jsonify({"error": "Message text required"}), 400

    if parent_id in ("", None):
        parent_id = None  # make sure it's null in DB

    conn = sqlite3.connect("forum.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (parent_id, text, timestamp) VALUES (?, ?, ?)",
        (parent_id, text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

if __name__ == "__main__":  # ✅ Correct spelling
    app.run(debug=True)
