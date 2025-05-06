from flask import Flask, request, jsonify, Response, render_template
import hashlib
import hmac
import time
import requests
import json
import random
import os

app = Flask(__name__)

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        VALID_API_KEYS = {config['apikey']: "active"}
except (FileNotFoundError, json.JSONDecodeError):
    VALID_API_KEYS = {os.getenv('API_KEY', 'xuankien1212'): "active"}

URL = "https://zingmp3.vn"
API_KEY = "X5BM3w8N7MKozC0B85o4KMlzLZKhV00y"
SECRET_KEY = "acOrvUS15XRW2o9JksiK1KgQ6Vbds8ZW"
VERSION = "1.11.11"

def get_hash256(string):
    return hashlib.sha256(string.encode()).hexdigest()

def get_hmac512(string, key):
    return hmac.new(key.encode(), string.encode(), hashlib.sha512).hexdigest()

def get_sig(path, params):
    param_string = ''.join(f"{key}={params[key]}" for key in sorted(params.keys()) if key in ["ctime", "id", "type", "page", "count", "version"])
    return get_hmac512(path + get_hash256(param_string), SECRET_KEY)

def get_cookie():
    response = requests.get(URL)
    return response.cookies.get_dict()

def request_zing_mp3(path, params):
    cookies = get_cookie()
    response = requests.get(f"{URL}{path}", params=params, cookies=cookies)
    return response.json()

def search_music(keyword):
    ctime = str(int(time.time()))
    path = "/api/v2/search"
    params = {
        "q": keyword,
        "type": "song",
        "count": 10,
        "ctime": ctime,
        "version": VERSION,
        "apiKey": API_KEY,
        "sig": get_sig(path, {
            "q": keyword,
            "type": "song",
            "count": 10,
            "ctime": ctime,
            "version": VERSION
        })
    }
    return request_zing_mp3(path, params)

def get_streaming_song(song_id):
    ctime = str(int(time.time()))
    path = "/api/v2/song/get/streaming"
    params = {
        "id": song_id,
        "ctime": ctime,
        "version": VERSION,
        "apiKey": API_KEY,
        "sig": get_sig(path, {
            "id": song_id,
            "ctime": ctime,
            "version": VERSION
        })
    }
    return request_zing_mp3(path, params)

def get_lyrics(song_id):
    try:
        response = requests.get(f"https://m.zingmp3.vn/xhr/lyrics/get-lyrics", params={"media_id": song_id})
        return response.json()
    except:
        return {"err": -1, "msg": "Không lấy được lời bài hát"}

def validate_api_key(api_key):
    if not api_key:
        return {"error": "Thiếu ApiKey", "status_code": 401}
    if api_key not in VALID_API_KEYS:
        return {"error": "ApiKey không hợp lệ", "status_code": 401}
    
    status = VALID_API_KEYS[api_key]
    if status == "inactive":
        return {"error": "ApiKey đã bị thay đổi", "status_code": 403}
    if status == "banned":
        return {"error": "ApiKey đã bị cấm", "status_code": 403}
    
    return {"valid": True}

def check_banned(player_id):
    url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "referer": "https://ff.garena.com/en/support/",
        "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json().get("data", {})
            is_banned = data.get("is_banned", 0)
            period = data.get("period", 0)
            result = {
                "credits": "Vũ Xuân Kiên (@xkprj)",
                "groupTelegram": "https://t.me/sharecodevn",
                "status": "Bị cấm" if is_banned else "Không bị cấm",
                "banPeriod": period if is_banned else 0,
                "uid": player_id,
                "isBanned": bool(is_banned)
            }
            return Response(json.dumps(result), mimetype="application/json")
        else:
            return Response(json.dumps({"error": "Không thể lấy dữ liệu từ máy chủ", "status_code": 500}), mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e), "status_code": 500}), mimetype="application/json")

def load_girl_images():
    try:
        with open('assets/girl.txt', 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def load_girl_videos():
    try:
        with open('assets/videogirl.txt', 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

@app.route("/check_ban", methods=["GET"])
def bancheck():
    api_key = request.args.get("apikey")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")
    player_id = request.args.get("uid", "")
    if not player_id:
        return Response(json.dumps({"error": "Yêu cầu ID người chơi", "status_code": 400}), mimetype="application/json")
    return check_banned(player_id)

@app.route("/zingmp3_search", methods=["GET"])
def zingmp3_search():
    api_key = request.args.get("apikey")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")
    keyword = request.args.get("keyword", "")
    if not keyword:
        return jsonify({"error": "Yêu cầu từ khóa"}), 400
    try:
        result = search_music(keyword)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "status_code": 500}), 500

@app.route("/zingmp3_download", methods=["GET"])
def zingmp3_download():
    api_key = request.args.get("apikey")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")
    song_id = request.args.get("song_id", "")
    if not song_id:
        return jsonify({"error": "Yêu cầu ID bài hát"}), 400
    try:
        streaming_info = get_streaming_song(song_id)
        if "data" in streaming_info:
            download_url = streaming_info["data"].get("streaming", "")
            if download_url:
                return jsonify({"download_url": download_url})
            else:
                return jsonify({"error": "Không tìm thấy URL tải xuống"}), 404
        else:
            return jsonify({"error": "Không thể lấy dữ liệu phát bài hát"}), 500
    except Exception as e:
        return jsonify({"error": str(e), "status_code": 500}), 500

@app.route("/random_girl_image", methods=["GET"])
def random_girl_image():
    api_key = request.args.get("apikey")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")
    images = load_girl_images()
    if not images:
        return jsonify({"error": "Không có ảnh nào trong danh sách"}), 404
    return jsonify({"image_url": random.choice(images)})

@app.route("/random_girl_video", methods=["GET"])
def random_girl_video():
    api_key = request.args.get("apikey")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")
    videos = load_girl_videos()
    if not videos:
        return jsonify({"error": "Không có video nào trong danh sách"}), 404
    return jsonify({"video_url": random.choice(videos)})

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

application = app
