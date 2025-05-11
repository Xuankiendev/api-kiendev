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
request_logs = []

for bp in [check_ban_bp, zingmp3_bp, random_media_bp, tiktok_bp, gemini_bp, screenshot_bp, text_to_audio_bp]:
    app.register_blueprint(bp)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot7687550929:AAEBNhw-76nKtpKYJ71Z6VV5eGOVsuZ4iBc/sendMessage?chat_id=-1002370415846&text={message}"
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
    request_logs.append({
        'endpoint': endpoint, 'method': method, 'ip': ip,
        'user_agent': user_agent, 'query': query, 'body': body, 'time': request_time
    })
    message = f"📊 New Request API 📊\n🔗 Link API: {request.host_url}\n🧪 Endpoint: {endpoint}\n📌 Method: {method}\n🔢 IP: {ip}\n👤 User-Agent: {user_agent}\n📝 Query: {query}\n🏃 Body: {body}\n🧭 Time: {request_time}"
    if len(message) > 4000:
        message = message[:3990] + "\n...(cắt bớt)"
    send_telegram_message(message)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    total_requests = len(request_logs)
    unique_ips = len(set(log['ip'] for log in request_logs))
    endpoint_counts = {}
    for log in request_logs:
        endpoint_counts[log['endpoint']] = endpoint_counts.get(log['endpoint'], 0) + 1
    return render_template('dashboard.html', total_requests=total_requests, unique_ips=unique_ips, endpoint_counts=endpoint_counts, logs=request_logs, domain=request.host_url.rstrip('/'))

@app.route('/apis')
def apis():
    return render_template('apis.html', domain=request.host_url.rstrip('/'))

if __name__ == '__main__':
    app.run(debug=True)
