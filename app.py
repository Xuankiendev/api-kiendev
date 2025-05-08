from flask import Flask, request, jsonify, Response, render_template
import hashlib
import hmac
import time
import requests
import json
import random
import os
import tempfile
from gtts import gTTS

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

API_KEYS = {os.getenv('API_KEY', 'xuankien1212'): "active"}

def check_key(api_key):
    if not api_key:
        return {"error": "Thiếu API Key", "status": 401}
    if api_key not in API_KEYS:
        return {"error": "API Key sai", "status": 401}
    return None

@app.route("/check_ban", methods=["GET"])
def check_ban():
    api_key = request.args.get("apikey")
    key_error = check_key(api_key)
    if key_error:
        return Response(json.dumps(key_error, ensure_ascii=False), mimetype="application/json", status=key_error["status"])
    
    uid = request.args.get("uid", "")
    if not uid:
        return Response(json.dumps({"error": "Cần UID người chơi", "status": 400}, ensure_ascii=False), mimetype="application/json", status=400)
    
    config = {
        "url": f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={uid}",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "referer": "https://ff.garena.com/en/support/",
            "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"
        }
    }
    try:
        response = requests.get(config["url"], headers=config["headers"], timeout=5)
        if response.status_code == 200:
            data = response.json().get("data", {})
            is_banned = data.get("is_banned", 0)
            period = data.get("period", 0)
            result = {
                "credits": "Vũ Xuân Kiên (@xkprj)",
                "telegram": "https://t.me/sharecodevn",
                "status": "Bị cấm" if is_banned else "Không cấm",
                "ban_time": period if is_banned else 0,
                "uid": uid,
                "is_banned": bool(is_banned)
            }
            return Response(json.dumps(result, ensure_ascii=False), mimetype="application/json")
        return Response(json.dumps({"error": "Không lấy được data", "status": 500}, ensure_ascii=False), mimetype="application/json", status=500)
    except Exception as e:
        return Response(json.dumps({"error": f"Lỗi server: {str(e)}", "status": 500}, ensure_ascii=False), mimetype="application/json", status=500)

@app.route("/zingmp3_search", methods=["GET"])
def zingmp3_search():
    config = {
        "url": "https://zingmp3.vn",
        "api_key": "X5BM3w8N7MKozC0B85o4KMlzLZKhV00y",
        "secret_key": "acOrvUS15XRW2o9JksiK1KgQ6Vbds8ZW",
        "version": "1.11.11",
        "path": "/api/v2/search",
        "count": 10,
        "type": "song"
    }

    def hash256(string):
        return hashlib.sha256(string.encode()).hexdigest()

    def hmac512(string, key):
        return hmac.new(key.encode(), string.encode(), hashlib.sha512).hexdigest()

    def get_sig(path, params):
        param_string = ''.join(f"{k}={params[k]}" for k in sorted(params) if k in ["ctime", "type", "page", "count", "version"])
        return hmac512(path + hash256(param_string), config["secret_key"])

    def get_cookie():
        try:
            response = requests.get(config["url"], timeout=5)
            return response.cookies.get_dict()
        except Exception:
            return {}

    def zing_request(path, params):
        cookies = get_cookie()
        try:
            response = requests.get(f"{config['url']}{path}", params=params, cookies=cookies, timeout=5)
            return response.json()
        except Exception:
            return {"error": "Lỗi API", "status": 500}

    api_key = request.args.get("apikey")
    key_error = check_key(api_key)
    if key_error:
        return Response(json.dumps(key_error, ensure_ascii=False), mimetype="application/json", status=key_error["status"])

    keyword = request.args.get("keyword", "")
    if not keyword:
        return Response(json.dumps({"error": "Cần từ khóa", "status": 400}, ensure_ascii=False), mimetype="application/json", status=400)

    try:
        ctime = str(int(time.time()))
        params = {
            "q": keyword,
            "type": config["type"],
            "count": config["count"],
            "ctime": ctime,
            "version": config["version"],
            "apiKey": config["api_key"],
            "sig": get_sig(config["path"], {
                "q": keyword,
                "type": config["type"],
                "count": config["count"],
                "ctime": ctime,
                "version": config["version"]
            })
        }
        result = zing_request(config["path"], params)
        return Response(json.dumps(result, ensure_ascii=False), mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": f"Lỗi server: {str(e)}", "status": 500}, ensure_ascii=False), mimetype="application/json", status=500)

@app.route("/zingmp3_download", methods=["GET"])
def zingmp3_download():
    config = {
        "url": "https://zingmp3.vn",
        "api_key": "X5BM3w8N7MKozC0B85o4KMlzLZKhV00y",
        "secret_key": "acOrvUS15XRW2o9JksiK1KgQ6Vbds8ZW",
        "version": "1.11.11",
        "path": "/api/v2/song/get/streaming"
    }

    def hash256(string):
        return hashlib.sha256(string.encode()).hexdigest()

    def hmac512(string, key):
        return hmac.new(key.encode(), string.encode(), hashlib.sha512).hexdigest()

    def get_sig(path, params):
        param_string = ''.join(f"{k}={params[k]}" for k in sorted(params) if k in ["ctime", "id", "version"])
        return hmac512(path + hash256(param_string), config["secret_key"])

    def get_cookie():
        try:
            response = requests.get(config["url"], timeout=5)
            return response.cookies.get_dict()
        except Exception:
            return {}

    def zing_request(path, params):
        cookies = get_cookie()
        try:
            response = requests.get(f"{config['url']}{path}", params=params, cookies=cookies, timeout=5)
            return response.json()
        except Exception:
            return {"error": "Lỗi API", "status": 500}

    api_key = request.args.get("apikey")
    key_error = check_key(api_key)
    if key_error:
        return Response(json.dumps(key_error, ensure_ascii=False), mimetype="application/json", status=key_error["status"])

    song_id = request.args.get("song_id", "")
    if not song_id:
        return Response(json.dumps({"error": "Cần ID bài hát", "status": 400}, ensure_ascii=False), mimetype="application/json", status=400)

    try:
        ctime = str(int(time.time()))
        params = {
            "id": song_id,
            "ctime": ctime,
            "version": config["version"],
            "apiKey": config["api_key"],
            "sig": get_sig(config["path"], {
                "id": song_id,
                "ctime": ctime,
                "version": config["version"]
            })
        }
        data = zing_request(config["path"], params)
        
        if data.get("err", -1) != 0 or not data.get("data"):
            return Response(json.dumps({"error": "Không tải được bài hát", "status": 500}, ensure_ascii=False), mimetype="application/json", status=500)
        
        audio_url = data["data"].get("320")
        quality = "320kbps"
        if audio_url == "VIP" or not audio_url:
            audio_url = data["data"].get("128")
            quality = "128kbps"
        
        if not audio_url:
            return Response(json.dumps({"error": "Không tìm thấy link tải", "status": 404}, ensure_ascii=False), mimetype="application/json", status=404)
        
        return Response(json.dumps({"download_url": audio_url, "quality": quality}, ensure_ascii=False), mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": f"Lỗi server: {str(e)}", "status": 500}, ensure_ascii=False), mimetype="application/json", status=500)

def load_media(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        return []

@app.route("/random_girl_image", methods=["GET"])
def random_girl_image():
    api_key = request.args.get("apikey")
    key_error = check_key(api_key)
    if key_error:
        return Response(json.dumps(key_error, ensure_ascii=False), mimetype="application/json", status=key_error["status"])

    images = load_media("assets/girl.txt")
    if not images:
        return Response(json.dumps({"error": "Không có ảnh", "status": 404}, ensure_ascii=False), mimetype="application/json", status=404)
    return Response(json.dumps({"image_url": random.choice(images)}, ensure_ascii=False), mimetype="application/json")

@app.route("/random_girl_video", methods=["GET"])
def random_girl_video():
    api_key = request.args.get("apikey")
    key_error = check_key(api_key)
    if key_error:
        return Response(json.dumps(key_error, ensure_ascii=False), mimetype="application/json", status=key_error["status"])

    videos = load_media("assets/videogirl.txt")
    if not videos:
        return Response(json.dumps({"error": "Không có video", "status": 404}, ensure_ascii=False), mimetype="application/json", status=404)
    return Response(json.dumps({"video_url": random.choice(videos)}, ensure_ascii=False), mimetype="application/json")

@app.route("/tiktok_download", methods=["GET"])
def tiktok_download():
    def download_tiktok(url):
        try:
            api_url = f"https://www.tikwm.com/api/?url={url}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json"
            }
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {"error": "Lỗi kết nối API TikTok", "status": 500}
            data = response.json()
            if data.get("code", -1) != 0:
                return {"error": "URL TikTok sai", "status": 400}
            if not data.get("data"):
                return {"error": "Không tìm thấy video", "status": 404}
            return data
        except Exception as e:
            return {"error": f"Lỗi server: {str(e)}", "status": 500}
    
    api_key = request.args.get("apikey")
    key_error = check_key(api_key)
    if key_error:
        return Response(json.dumps(key_error, ensure_ascii=False), mimetype="application/json", status=key_error["status"])
    
    tiktok_url = request.args.get("url", "")
    if not tiktok_url:
        return Response(json.dumps({"error": "Cần URL TikTok", "status": 400}, ensure_ascii=False), mimetype="application/json", status=400)
    
    result = download_tiktok(tiktok_url)
    return Response(json.dumps(result, ensure_ascii=False), mimetype="application/json", status=result.get("status", 200))

@app.route("/chat_gemini", methods=["GET"])
def chat_gemini():
    api_key = request.args.get("apikey")
    key_error = check_key(api_key)
    if key_error:
        return Response(json.dumps(key_error, ensure_ascii=False), mimetype="application/json", status=key_error["status"])

    ask = request.args.get("ask", "")
    if not ask:
        return Response(json.dumps({"error": "Cần câu hỏi", "status": 400}, ensure_ascii=False), mimetype="application/json", status=400)

    prompt = request.args.get("prompt", "")

    try:
        api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=AIzaSyC5VvVGBk3T0TzfF_JCaDTDPAW97oRhdrc"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}] if prompt else [{"role": "user", "parts": [{"text": ask}]}]
        }
        response = requests.post(api_url, headers=headers, data=json.dumps(data), timeout=5)
        if response.status_code != 200:
            return Response(json.dumps({"error": "Lỗi API Gemini", "status": 500}, ensure_ascii=False), mimetype="application/json", status=500)
        
        response_json = response.json()
        if 'candidates' in response_json and response_json['candidates']:
            answer = response_json['candidates'][0]['content']['parts'][0]['text']
            result = {
                "query": ask,
                "answer": answer,
                "prompt": prompt or "Không có prompt"
            }
            return Response(json.dumps(result, ensure_ascii=False), mimetype="application/json")
        return Response(json.dumps({"error": "Không có trả lời từ Gemini", "status": 500}, ensure_ascii=False), mimetype="application/json", status=500)
    except Exception as e:
        return Response(json.dumps({"error": f"Lỗi server: {str(e)}", "status": 500}, ensure_ascii=False), mimetype="application/json", status=500)

@app.route("/screenshot", methods=["GET"])
def screenshot():
    api_key = request.args.get("apikey")
    key_error = check_key(api_key)
    if key_error:
        return Response(json.dumps(key_error, ensure_ascii=False), mimetype="application/json", status=key_error["status"])

    url = request.args.get("url", "")
    if not url:
        return Response(json.dumps({"error": "Cần URL để chụp ảnh", "status": 400}, ensure_ascii=False), mimetype="application/json", status=400)

    try:
        screenshot_url = f"https://api.site-shot.com/?url={url}&userkey=MAAIEYKBJAIDBB7IYJLBPSC6LV"
        response = requests.get(screenshot_url, timeout=10)
        if response.status_code != 200:
            return Response(json.dumps({"error": "Không chụp được ảnh", "status": 500}, ensure_ascii=False), mimetype="application/json", status=500)
        return Response(response.content, mimetype=response.headers['Content-Type'])
    except Exception as e:
        return Response(json.dumps({"error": f"Lỗi server: {str(e)}", "status": 500}, ensure_ascii=False), mimetype="application/json", status=500)

@app.route("/text_to_audio", methods=["GET"])
def text_to_audio():
    api_key = request.args.get("apikey")
    key_error = check_key(api_key)
    if key_error:
        return Response(json.dumps(key_error, ensure_ascii=False), mimetype="application/json", status=key_error["status"])

    text = request.args.get("text", "")
    if not text:
        return Response(json.dumps({"error": "Cần văn bản", "status": 400}, ensure_ascii=False), mimetype="application/json", status=400)

    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            audio_file = temp_file.name
        tts = gTTS(text=text, lang='vi')
        tts.save(audio_file)
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        return Response(audio_data, mimetype="audio/mpeg")
    except Exception as e:
        return Response(json.dumps({"error": f"Lỗi chuyển giọng: {str(e)}", "status": 500}, ensure_ascii=False), mimetype="application/json", status=500)
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
