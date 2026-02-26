from flask import Flask, render_template, request
from cryptography.fernet import Fernet
import base64
import hashlib
import qrcode
import os
import uuid
import json
import io

app = Flask(__name__)

# --------- Helper: Generate Key From Password ---------
def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

# --------- Encrypt Function ---------
def encrypt_message(message, password):
    key = generate_key(password)
    cipher = Fernet(key)
    return cipher.encrypt(message.encode()).decode()

# --------- Decrypt Function ---------
def decrypt_message(encrypted_message, password):
    key = generate_key(password)
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_message.encode()).decode()

# --------- Generate QR (IN MEMORY - No File Saving) ---------
def generate_qr(data):
    img = qrcode.make(data)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()

# --------- HOME ROUTE ---------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        message = request.form.get("message")
        password = request.form.get("password")

        if not message or not password:
            return render_template("index.html", error="Please enter all fields")

        encrypted = encrypt_message(message, password)

        # Create unique ID
        unique_id = str(uuid.uuid4())

        # Store encrypted data in temporary file (Render supports /tmp)
        data_path = f"/tmp/{unique_id}.json"
        with open(data_path, "w") as f:
            json.dump({"encrypted": encrypted}, f)

        # Generate QR with unique link
        qr_link = f"https://secure-qr-code-generator.onrender.com/decrypt/{unique_id}"
        qr_image = generate_qr(qr_link)

        return render_template("index.html", qr_image=qr_image)

    return render_template("index.html")


# --------- DECRYPT ROUTE ---------
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


# --------- Run App (Only for Local Testing) ---------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)