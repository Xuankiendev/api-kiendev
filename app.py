from flask import Flask, render_template, request
from apis.check_ban import check_ban_bp
from apis.zingmp3 import zingmp3_bp
from apis.random_media import random_media_bp
from apis.tiktok import tiktok_bp
from apis.gemini import gemini_bp
from apis.screenshot import screenshot_bp
from apis.text_to_audio import text_to_audio_bp
import requests
import datetime

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

for bp in [check_ban_bp, zingmp3_bp, random_media_bp, tiktok_bp, gemini_bp, screenshot_bp, text_to_audio_bp]:
    app.register_blueprint(bp)

def send_telegram_message(message):
    url = "https://api.telegram.org/bot7687550929:AAEBNhw-76nKtpKYJ71Z6VV5eGOVsuZ4iBc/sendMessage?chat_id=-1002370415846&text=" + message
    requests.get(url)

@app.before_request
def log_request():
    endpoint = request.path
    method = request.method
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Không có')
    query = request.args.to_dict()
    try:
        body = request.get_json(force=True)
    except:
        body = {}

    request_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    message = (
        f"📊 New Request API 📊\n"
        f"🔗 Link API: https://api-kiendev.vercel.app"
        f"⛔ Endpoint: {endpoint}\n"
        f"📌 Method: {method}\n"
        f"🔢 IP: {ip}\n"
        f"👤 User-Agent: {user_agent}\n"
        f"📝 Query: {query}\n"
        f"🏃 Body: {body}\n"
        f"🧭 Time: {request_time}"
    )

    if len(message) > 4000:
        message = message[:3990] + "\n...(cắt bớt)"

    send_telegram_message(message)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
