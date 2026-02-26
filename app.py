from flask import Flask, render_template, request, redirect, url_for
from cryptography.fernet import Fernet
import qrcode
import uuid
import os

app = Flask(__name__)

# Temporary storage (resets if server restarts)
messages = {}

# ---------------- HOME PAGE ----------------
@app.route('/')
def home():
    return render_template("index.html")

# ---------------- GENERATE QR ----------------
@app.route('/generate', methods=['POST'])
def generate():

    message = request.form.get("message")
    password = request.form.get("password")

    if not message or not password:
        return "Message and password required"

    # Create encryption key
    key = Fernet.generate_key()
    cipher = Fernet(key)

    # Encrypt message
    encrypted_message = cipher.encrypt(message.encode())

    # Create unique ID
    unique_id = str(uuid.uuid4())

    # Store data temporarily
    messages[unique_id] = {
        "encrypted": encrypted_message,
        "key": key,
        "password": password
    }

    # Create QR URL
    qr_url = request.host_url + "view/" + unique_id

    # Generate QR
    img = qrcode.make(qr_url)

    # Ensure static folder exists
    if not os.path.exists("static"):
        os.makedirs("static")

    img.save("static/qr.png")

    return render_template("qr.html")


# ---------------- PASSWORD PAGE ----------------
@app.route('/view/<unique_id>', methods=['GET', 'POST'])
def view_message(unique_id):

    if unique_id not in messages:
        return "Invalid or expired QR code"

    if request.method == "POST":
        entered_password = request.form.get("password")

        if entered_password == messages[unique_id]["password"]:
            cipher = Fernet(messages[unique_id]["key"])
            decrypted_message = cipher.decrypt(
                messages[unique_id]["encrypted"]
            ).decode()

            return render_template("message.html", message=decrypted_message)
        else:
            return render_template("password.html", error="Invalid Password")

    return render_template("password.html")


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)