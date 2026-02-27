from flask import Flask, render_template, request
from cryptography.fernet import Fernet
import qrcode
import io
import base64
import hashlib

app = Flask(__name__)


def generate_key_from_password(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    message = request.form.get("message")
    password = request.form.get("password")

    if not message or not password:
        return "Message and password required"

    # Generate key from password
    key = generate_key_from_password(password)
    f = Fernet(key)

    encrypted_message = f.encrypt(message.encode()).decode()

    # QR will contain encrypted message directly
    qr = qrcode.make(encrypted_message)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    img_str = base64.b64encode(buffer.getvalue()).decode()

    return render_template("qr.html", qr_image=img_str)


@app.route("/decrypt", methods=["GET", "POST"])
def decrypt():

    if request.method == "POST":
        encrypted_message = request.form.get("encrypted_message")
        password = request.form.get("password")

        try:
            key = generate_key_from_password(password)
            f = Fernet(key)
            decrypted = f.decrypt(encrypted_message.encode()).decode()
            return render_template("message.html", message=decrypted)
        except Exception:
            return "Wrong Password or Invalid QR"

    return render_template("password.html")


if __name__ == "__main__":
    app.run(debug=True)