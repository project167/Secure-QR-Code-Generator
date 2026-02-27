from flask import Flask, render_template, request
from cryptography.fernet import Fernet
import qrcode
import io
import base64
import urllib.parse

app = Flask(__name__)

messages = {}

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    message = request.form.get("message")
    password = request.form.get("password")

    if not message or not password:
        return "Message and password required"

    key = Fernet.generate_key()
    f = Fernet(key)

    encrypted_message = f.encrypt(message.encode()).decode()

    # URL safe encode
    safe_token = urllib.parse.quote(encrypted_message)

    messages[encrypted_message] = {
        "password": password,
        "key": key.decode()
    }

    link = request.url_root + "decrypt/" + safe_token

    qr = qrcode.make(link)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)

    img_str = base64.b64encode(buffer.getvalue()).decode()

    return render_template("qr.html", qr_image=img_str)


@app.route("/decrypt/<path:token>", methods=["GET", "POST"])
def decrypt(token):
    # Decode URL safe token
    token = urllib.parse.unquote(token)

    if token not in messages:
        return "Invalid or expired QR"

    if request.method == "POST":
        entered_password = request.form.get("password")

        if entered_password == messages[token]["password"]:
            key = messages[token]["key"].encode()
            f = Fernet(key)
            decrypted_message = f.decrypt(token.encode()).decode()

            return render_template("message.html", message=decrypted_message)
        else:
            return "Wrong Password"

    return render_template("password.html")


if __name__ == "__main__":
    app.run(debug=True)