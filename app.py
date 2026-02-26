from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
import base64
import hashlib
import qrcode
import os
import uuid
import json

app = Flask(__name__)

# ---------- KEY GENERATION ----------
def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

# ---------- ENCRYPT ----------
def encrypt_message(message, password):
    key = generate_key(password)
    cipher = Fernet(key)
    return cipher.encrypt(message.encode()).decode()

# ---------- DECRYPT ----------
def decrypt_message(encrypted_message, password):
    key = generate_key(password)
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_message.encode()).decode()

# ---------- GENERATE QR ----------
def generate_qr(link):
    img = qrcode.make(link)
    img.save("/tmp/qr.png")

# ---------- SERVE QR ----------
@app.route("/qr")
def serve_qr():
    return send_file("/tmp/qr.png", mimetype="image/png")

# ---------- HOME ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        message = request.form.get("message")
        password = request.form.get("password")

        if not message or not password:
            return render_template("index.html", error="Enter all fields")

        encrypted = encrypt_message(message, password)

        # Unique ID for each message
        unique_id = str(uuid.uuid4())

        # Save encrypted message in /tmp
        data_path = f"/tmp/{unique_id}.json"
        with open(data_path, "w") as f:
            json.dump({"encrypted": encrypted}, f)

        # Generate QR with unique link
        qr_link = f"https://secure-qr-code-generator.onrender.com/decrypt/{unique_id}"
        generate_qr(qr_link)

        return render_template("index.html", qr_generated=True)

    return render_template("index.html")

# ---------- DECRYPT ----------
@app.route("/decrypt/<unique_id>", methods=["GET", "POST"])
def decrypt_page(unique_id):
    result = ""
    data_path = f"/tmp/{unique_id}.json"

    if not os.path.exists(data_path):
        return "Message expired or invalid QR"

    if request.method == "POST":
        password = request.form.get("password")

        with open(data_path, "r") as f:
            data = json.load(f)

        encrypted_text = data["encrypted"]

        try:
            result = decrypt_message(encrypted_text, password)
        except:
            result = "Invalid Password"

    return render_template("decrypt.html", result=result)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run()