from flask import Flask, request, render_template_string, send_file
import qrcode
import uuid
import os
import json

app = Flask(__name__)

BASE_URL = "https://valentine-app.onrender.com"
DATA_FILE = "messages.json"
QR_FOLDER = "qr_codes"
UPLOAD_FOLDER = "uploads"

os.makedirs(QR_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_messages():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_messages(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# =============================
# Trang tạo QR + Upload ảnh
# =============================
@app.route("/create", methods=["GET", "POST"])
def create():

    if request.method == "POST":

        name = request.form.get("name")
        message = request.form.get("message")
        image = request.files.get("image")

        uid = str(uuid.uuid4())

        image_filename = None
        if image:
            image_filename = f"{uid}.jpg"
            image.save(os.path.join(UPLOAD_FOLDER, image_filename))

        messages = load_messages()
        messages[uid] = {
            "name": name,
            "message": message,
            "image": image_filename
        }
        save_messages(messages)

        url = f"{BASE_URL}/valentine/{uid}"

        qr = qrcode.make(url)
        path = f"{QR_FOLDER}/{uid}.png"
        qr.save(path)

        return send_file(path, mimetype="image/png")

    return """
    <h2>Create Valentine QR ❤️</h2>
    <form method="POST" enctype="multipart/form-data">
        Name:<br>
        <input name="name"><br><br>
        Message:<br>
        <textarea name="message"></textarea><br><br>
        Upload Photo:<br>
        <input type="file" name="image"><br><br>
        <button type="submit">Generate QR</button>
    </form>
    """

# =============================
# Trang Valentine đẹp
# =============================
@app.route("/valentine/<uid>")
def valentine(uid):

    messages = load_messages()
    data = messages.get(uid)

    if not data:
        return "Invalid link"

    image_html = ""
    if data["image"]:
        image_html = f'<img src="/uploads/{data["image"]}" class="photo">'

    html = f"""
    <html>
    <head>
        <title>Happy Valentine's Day ❤️</title>

        <style>
            body {{
                margin:0;
                overflow:hidden;
                font-family: Arial;
                background: linear-gradient(135deg,#ff758c,#ff7eb3);
                color:white;
                text-align:center;
            }}

            .container {{
                position:relative;
                top:100px;
                z-index:2;
            }}

            .card {{
                background: rgba(255,255,255,0.2);
                padding:40px;
                border-radius:20px;
                width:60%;
                margin:auto;
                backdrop-filter: blur(10px);
            }}

            .photo {{
                width:250px;
                border-radius:20px;
                margin-top:20px;
            }}

            /* ❤️ Floating Hearts */
            .heart {{
                position:absolute;
                color:white;
                font-size:24px;
                animation: float 6s linear infinite;
            }}

            @keyframes float {{
                0% {{ transform: translateY(100vh); opacity:0; }}
                50% {{ opacity:1; }}
                100% {{ transform: translateY(-10vh); opacity:0; }}
            }}
        </style>
    </head>

    <body>

        <!-- 🎵 Nhạc nền -->
        <audio autoplay loop>
            <source src="/music" type="audio/mp3">
        </audio>

        <div class="container">
            <div class="card">
                <h1>Happy Valentine's Day ❤️</h1>
                <h2>Dear {data["name"]}</h2>
                <p>{data["message"]}</p>
                {image_html}
            </div>
        </div>

        <script>
            function createHeart() {{
                const heart = document.createElement("div");
                heart.classList.add("heart");
                heart.innerHTML = "❤️";
                heart.style.left = Math.random() * 100 + "vw";
                heart.style.animationDuration = (Math.random()*3+3) + "s";
                document.body.appendChild(heart);

                setTimeout(()=>heart.remove(),6000);
            }}

            setInterval(createHeart,300);
        </script>

    </body>
    </html>
    """

    return render_template_string(html)

# =============================
# Serve ảnh upload
# =============================
@app.route("/uploads/<filename>")
def uploads(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

# =============================
# Serve nhạc nền
# =============================
@app.route("/music")
def music():
    return send_file("music.mp3")

if __name__ == "__main__":
    app.run(debug=True)
