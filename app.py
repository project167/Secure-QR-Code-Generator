from flask import Flask, render_template, request, send_from_directory
from encrypt_qr import encrypt_message, generate_qr
from decrypt_qr import decrypt_message

app = Flask(__name__)

# Temporary storage (for demo project)
encrypted_data_store = ""

# Serve QR image
@app.route('/secure_qr.png')
def serve_qr():
    return send_from_directory('.', 'secure_qr.png')


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

                # ⚠️ CHANGE THIS TO YOUR PC IP
                generate_qr("https://secure-qr-code-generator.onrender.com/decrypt")
                qr_generated = True

    return render_template("index.html", qr_generated=qr_generated)


# DECRYPT PAGE (Opened on Mobile)
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)