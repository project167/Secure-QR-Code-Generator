from flask import Flask, render_template, request, send_file
from encrypt_qr import encrypt_message, generate_qr
from decrypt_qr import decrypt_message
import os

app = Flask(__name__)

# Temporary storage (NOTE: resets if server restarts)
encrypted_data_store = ""


# Serve QR image from /tmp (Render writable directory)
@app.route('/secure_qr.png')
def serve_qr():
    file_path = "/tmp/secure_qr.png"
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "QR Code not found. Please generate again."


# HOME PAGE
@app.route("/", methods=["GET", "POST"])
def index():
    global encrypted_data_store
    qr_generated = False

    if request.method == "POST":
        if "generate" in request.form:
            message = request.form.get("message")
            password = request.form.get("password")

            if message and password:
                encrypted = encrypt_message(message, password)
                encrypted_data_store = encrypted

                # Generate QR pointing to your live decrypt page
                generate_qr("https://secure-qr-code-generator.onrender.com/decrypt")

                qr_generated = True

    return render_template("index.html", qr_generated=qr_generated)


# DECRYPT PAGE
@app.route("/decrypt", methods=["GET", "POST"])
def decrypt_page():
    global encrypted_data_store
    result = ""

    if request.method == "POST":
        password = request.form.get("password")

        if password:
            try:
                result = decrypt_message(encrypted_data_store, password)
            except:
                result = "Wrong Password or Invalid QR"

    return render_template("decrypt.html", result=result)


# IMPORTANT: Render requires dynamic PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)