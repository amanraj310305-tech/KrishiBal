import os
import random
import string
from authlib.integrations.flask_client import OAuth
from flask import redirect, session
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from gtts import gTTS
from groq import Groq
import sqlite3
from datetime import datetime
import firebase_admin
from news import get_farming_news, get_government_schemes, search_news
from firebase_admin import credentials, firestore, auth
import smtplib
from email.mime.text import MIMEText





from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

# Import your modules
import crop_recom_final  # your crop recommender code
import imagefinal        # your plant disease prediction code

app = Flask(__name__)
# ---------- Firebase Setup ----------
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'

app.secret_key = "dev-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(BASE_DIR, "firebase_key.json")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()
oauth = OAuth(app)

oauth.register(
    name="google",
    client_id="420545816774-5nk6urhk6mu907r7mgshqhcv2a269qlq.apps.googleusercontent.com",
    client_secret="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",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


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

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_AUDIO'] = {'webm', 'wav', 'mp3', 'm4a'}
app.config['ALLOWED_IMAGE'] = {'png', 'jpg', 'jpeg'}

# ✅ Groq API for chatbot
api_key = "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"
groq_client = Groq(api_key=api_key)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs("static/audio", exist_ok=True)

# ---------- Utilities ----------
def allowed_file(filename, allowed_ext):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext


def text_to_audio(text, filename):
    tts = gTTS(text)
    audio_path = os.path.join("static/audio", f"{filename}.mp3")
    tts.save(audio_path)
    return audio_path

# ---------- Chatbot ----------
def transcribe_audio_groq(filepath):
    with open(filepath, "rb") as f:
        response = groq_client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=f,
        )
    return response.text

def get_answer_groq(question):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful agriculture chatbot for Indian farmers."},
                {"role": "user", "content": "Give a Brief Of Agriculture Seasons in India"},
                {"role": "system", "content": "In India, the agricultural season consists of three major seasons: the Kharif, the Rabi, and the Zaid."},
                {"role": "user", "content": question}
            ],
        )
    except Exception:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful agriculture chatbot for Indian farmers."},
                {"role": "user", "content": "Give a Brief Of Agriculture Seasons in India"},
                {"role": "system", "content": "In India, the agricultural season consists of three major seasons: the Kharif, the Rabi, and the Zaid."},
                {"role": "user", "content": question}
            ],
        )
    return response.choices[0].message.content

# ---------- Routes ----------
# ---------- Marketplace ----------
@app.route("/marketplace")
def marketplace():
    user = session.get("user")
    return render_template("marketplace.html", user=user)


@app.route("/add-product", methods=["POST"])
def add_product():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401

    data = request.json

    db.collection("products").add({
        "name": data.get("name"),
        "category": data.get("category"),  # sell / buy
        "price": data.get("price"),
        "quantity": data.get("quantity"),
        "seller": session["user"]["name"],
        "email": session["user"]["email"],
        "timestamp": datetime.now()
    })

    return jsonify({"success": True})


@app.route("/get-products")
def get_products():
    docs = db.collection("products").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
    products = []
    for doc in docs:
        products.append(doc.to_dict())
    return jsonify(products)

@app.route('/news')
def news_page():
    return render_template('news.html')


@app.route('/get-news', methods=['GET'])
def get_news():
    news_data = get_farming_news()
    return jsonify(news_data)


@app.route('/get-schemes', methods=['GET'])
def get_schemes():
    schemes_data = get_government_schemes()
    return jsonify(schemes_data)


@app.route('/search-news', methods=['POST'])
def search_farming_news():
    query = request.form.get('query')
    if not query:
        return jsonify({'success': False, 'error': 'Query is required'})

    search_results = search_news(query)
    return jsonify(search_results)
@app.route("/")
def index():
    user = session.get("user")
    return render_template("index.html", user=user)

@app.route("/login")
def login():
    return render_template("login.html")
@app.route("/auth/google")
def auth_google():
    redirect_uri = url_for("auth_google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)
@app.route("/auth/google/callback")
def auth_google_callback():
    token = oauth.google.authorize_access_token()
    user = token["userinfo"]

    session["user"] = {
        "email": user["email"],
        "name": user["name"],
        "picture": user["picture"]
    }

    # Save login in Firebase (backup)
    db.collection("logins").add({
        "email": user["email"],
        "name": user["name"],
        "timestamp": datetime.now()
    })

    return redirect("/")





# Chatbot route
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route('/chat', methods=['POST'])
def chat():
    if 'audio' in request.files:
        audio = request.files['audio']
        if audio and allowed_file(audio.filename, app.config['ALLOWED_AUDIO']):
            filename = secure_filename(audio.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio.save(filepath)
            transcription = transcribe_audio_groq(filepath)
            answer = get_answer_groq(transcription)
            voice_filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            text_to_audio(answer, voice_filename)
            return jsonify({
                'text': f"🎤 Transcribed: {transcription}\n\n🤖 Answer: {answer}",
                'voice': url_for('static', filename='audio/' + voice_filename + '.mp3')
            })

    elif 'text' in request.form:
        question = request.form['text']
        answer = get_answer_groq(question)
        voice_filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        text_to_audio(answer, voice_filename)
        return jsonify({
            'text': answer,
            'voice': url_for('static', filename='audio/' + voice_filename + '.mp3')
        })

    return jsonify({'text': 'No valid input found'}), 400

# Crop Recommender
# ---------- Crop Recommender ----------
@app.route('/crop-recommender', methods=['POST'])
def crop_recommender():
    district = request.form.get('district', '').strip()
    month = request.form.get('month', '').strip()

    if not district or not month:
        return jsonify({'error': 'Please provide both district and month.'}), 400

    # Convert month name to number if needed
    month_num = None
    try:
        month_num = int(month)
    except ValueError:
        # Try parsing month name
        MONTH_WORDS = {
            "january":1,"jan":1,"february":2,"feb":2,"march":3,"mar":3,"april":4,"apr":4,
            "may":5,"june":6,"jun":6,"july":7,"jul":7,"august":8,"aug":8,"september":9,"sep":9,"sept":9,
            "october":10,"oct":10,"november":11,"nov":11,"december":12,"dec":12
        }
        month_num = MONTH_WORDS.get(month.lower())
        if month_num is None:
            return jsonify({'error': f'Invalid month: {month}'}), 400

    # Get recommendation from your crop module
    # Get recommendation from your crop module
    recommendation = crop_recom_final.recommend_crop(district, month_num)

    return jsonify({'text': recommendation})
# ---------- Plant Disease Detection ----------
# ---------- Plant Disease Detection ----------
@app.route('/predict-disease', methods=['POST'])
def predict_disease():

    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']
    if file.filename == "":
        return jsonify({"error": "Empty file"}), 400
    if not allowed_file(file.filename, app.config['ALLOWED_IMAGE']):
        return jsonify({"error": "Invalid image type"}), 400

    # Get prediction (dict with disease + cure)
    result = imagefinal.predict(file)

    # Explicitly ensure both keys exist
    disease = result.get("disease", "Unknown")
    cure = result.get("cure", "Cure information not available")

    return jsonify({
        "disease": disease,
        "cure": cure
    })

# ---------- Forum ----------
@app.route('/forum')
def forum():
    return render_template('forum.html')

@app.route("/messages", methods=["GET"])
def get_messages():
    docs = db.collection("messages").order_by("timestamp").stream()
    messages = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        messages.append(data)
    return jsonify(messages)
@app.route("/messages", methods=["POST"])
def post_message():
    data = request.json
    text = data.get("text")
    parent_id = data.get("parent_id")

    if not text:
        return jsonify({"error": "Message text required"}), 400

    db.collection("messages").add({
        "text": text,
        "parent_id": parent_id,
        "timestamp": datetime.now()
    })

    return jsonify({"status": "success"})
if __name__== '__main__':
    app.run(debug=True)
