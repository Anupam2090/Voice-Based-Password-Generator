from flask import Flask, render_template, request, redirect, url_for, session,flash
import os
from audio_password import generate_password_from_audio
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------- Routes -------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    if 'audio' not in request.files:
        flash("❌ No audio file uploaded.")
        return redirect(url_for('index'))

    # Check if already registered
    if os.path.exists("stored_password.txt"):
        flash("⚠️ User already registered. Please log in.")
        return redirect(url_for('index'))

    file = request.files['audio']
    path = os.path.join(app.config['UPLOAD_FOLDER'], 'register.wav')
    file.save(path)

    password = generate_password_from_audio(path)
    with open("stored_password.txt", "w") as f:
        f.write(password)

    flash("✅ Registered successfully! You can now log in.")
    return redirect(url_for('index'))



@app.route('/login', methods=['POST'])
def login():
    if 'audio' not in request.files:
        flash("❌ No file uploaded.")
        return redirect(url_for('index'))

    file = request.files['audio']
    path = os.path.join(app.config['UPLOAD_FOLDER'], 'login.wav')
    file.save(path)

    login_password = generate_password_from_audio(path)

    # ✅ Handle no registered audio (file not found)
    if not os.path.exists("stored_password.txt"):
        flash("❌ No registered user found. Please register first.")
        return redirect(url_for('index'))

    with open("stored_password.txt", "r") as f:
        stored_password = f.read()

    if login_password == stored_password:
        session['authenticated'] = True
        return redirect(url_for('dashboard'))
    else:
        flash("❌ Access Denied: Password does not match.")
        return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    if os.path.exists("stored_password.txt"):
        os.remove("stored_password.txt")
    flash("Logged out and audio removed. Please register again.")
    return redirect(url_for('index'))

# ------------------- Run App -------------------

if __name__ == '__main__':
    app.run(debug=True)
