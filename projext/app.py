from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from googletrans import Translator
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "sabarish"

# Firebase Configuration
firebaseConfig = {
    "apiKey": "AIzaSyASjOmonau3_SFB-W7jzmLn_kvxAhugMJo",
    "authDomain": "translator-eb5a7.firebaseapp.com",
    "projectId": "translator-eb5a7",
    "storageBucket": "translator-eb5a7.firebasestorage.app",
    "messagingSenderId": "437614700636",
    "appId": "1:437614700636:web:2399b1594f65585dbc5e99",
    "measurementId": "G-X0E3HX424F",
    "databaseURL": "https://translator-eb5a7.firebaseio.com"  
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

cred = credentials.Certificate("D:/GitHub/Game/projext/translator-eb5a7-firebase-adminsdk-fbsvc-fb535b5450.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# MONGO_URI = "mongodb+srv://bitsathyattendance:5HuQI38XLYhZGWD1@bittools.uovd9.mongodb.net/translatorDB?retryWrites=true&w=majority&appName=bittools"

# MongoDB Connection
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["translatorDB"]
translations_collection = mongo_db["translations"]

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password == confirm_password:
            try:
                user = auth.create_user_with_email_and_password(email, password)
                user_info = {
                    "email": email,
                    "uid": user["localId"]
                }
                db.collection("users").document(user["localId"]).set(user_info)
                return redirect(url_for('index'))
            except Exception as e:
                return str(e)
        else:
            return "Passwords do not match!"
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        session['user'] = user['idToken']
        session['uid'] = user['localId'] 
        return redirect(url_for('home'))
    except Exception as e:
        return str(e)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        try:
            auth.send_password_reset_email(email)
            flash('Password reset email sent!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(str(e), 'error')
    return render_template('forgot_password.html')

@app.route('/home')
def home():
    if 'user' in session:
        return render_template('home.html')
    return redirect(url_for('index'))

@app.route('/translate', methods=['GET', 'POST'])
def translate():
    if 'user' not in session:
        return redirect(url_for('index'))

    translated_text = ""
    user_id = session['uid']

    # Fetch user's email from Firestore
    user_doc = db.collection("users").document(user_id).get()
    email = user_doc.to_dict().get("email", "Unknown") if user_doc.exists else "Unknown"
    
    if request.method == 'POST':
        text = request.form['text']
        target_lang = request.form['target_lang']
        translator = Translator()
        translated_text = translator.translate(text, dest=target_lang).text

        # Store translation in MongoDB
        translations_collection.insert_one({
            "user_id": user_id,
            "email": email,
            "original_text": text,
            "translated_text": translated_text,
            "target_lang": target_lang
        })

    # Retrieve user's past translations
    user_translations = list(translations_collection.find({"user_id": user_id}))

    return render_template('translator.html', translated_text=translated_text, user_translations=user_translations)



@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('uid', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)