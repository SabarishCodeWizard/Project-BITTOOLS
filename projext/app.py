from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from googletrans import Translator

app = Flask(__name__)
app.secret_key = "sabarish"

firebaseConfig = {
    "apiKey": "AIzaSyASjOmonau3_SFB-W7jzmLn_kvxAhugMJo",
    "authDomain": "translator-eb5a7.firebaseapp.com",
    "projectId": "translator-eb5a7",
    "storageBucket": "translator-eb5a7.firebasestorage.app",
    "messagingSenderId": "437614700636",
    "appId": "1:437614700636:web:2399b1594f65585dbc5e99",
    "measurementId": "G-X0E3HX424F",
    "databaseURL": "https://translator-eb5a7.firebaseio.com"  # Add this line
}


firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

cred = credentials.Certificate("D:/GitHub/Game/projext/translator-eb5a7-firebase-adminsdk-fbsvc-fb535b5450.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

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
    translated_text = ""
    if request.method == 'POST':
        text = request.form['text']
        target_lang = request.form['target_lang']
        translator = Translator()
        translated_text = translator.translate(text, dest=target_lang).text
    return render_template('translator.html', translated_text=translated_text)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
