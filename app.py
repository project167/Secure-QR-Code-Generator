from flask import Flask, render_template, request
from cryptography.fernet import Fernet
import base64
import hashlib
import qrcode
import io

app = Flask(__name__)

# Generate key from password
def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

# Encrypt
def encrypt_message(message, password):
    key = generate_key(password)
    cipher = Fernet(key)
    return cipher.encrypt(message.encode()).decode()

# Decrypt
def decrypt_message(encrypted_message, password):
    key = generate_key(password)
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_message.encode()).decode()

@app.route("/", methods=["GET", "POST"])
def index():
    qr_image = None

    if request.method == "POST":
        message = request.form.get("message")
        password = request.form.get("password")

        if message and password:
            encrypted = encrypt_message(message, password)

            # QR contains encrypted text directly
            img = qrcode.make(encrypted)

            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            qr_image = base64.b64encode(buffer.getvalue()).decode()

    return render_template("index.html", qr_image=qr_image)

@app.route("/decrypt", methods=["POST"])
def decrypt():
    encrypted = request.form.get("encrypted")
    password = request.form.get("password")

    try:
        message = decrypt_message(encrypted, password)
        return f"<h2>Decrypted Message:</h2><p>{message}</p>"
    except:
        return "<h2>Invalid Password</h2>"

if __name__ == "__main__":
    app.run()