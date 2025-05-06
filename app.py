from flask import Flask, request, jsonify, Response, render_template
import hashlib
import hmac
import time
import requests
import json
import random
import os

app = Flask(__name__)

# API Key Validation
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        VALID_API_KEYS = {config['apikey']: "active"}
except (FileNotFoundError, json.JSONDecodeError):
    VALID_API_KEYS = {os.getenv('API_KEY', 'xuankien1212'): "active"}

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

@app.route("/check_ban", methods=["GET"])
def bancheck():
    def check_banned(player_id):
        config = {
            "url": f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}",
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
    config = {
        "URL": "https://zingmp3.vn",
        "API_KEY": "X5BM3w8N7MKozC0B85o4KMlzLZKhV00y",
        "SECRET_KEY": "acOrvUS15XRW2o9JksiK1KgQ6Vbds8ZW",
        "VERSION": "1.11.11",
        "PATH": "/api/v2/search",
        "COUNT": 10,
        "TYPE": "song"
    }

    def get_hash256(string):
        return hashlib.sha256(string.encode()).hexdigest()

    def get_hmac512(string, key):
        return hmac.new(key.encode(), string.encode(), hashlib.sha512).hexdigest()

    def get_sig(path, params):
        param_string = ''.join(f"{key}={params[key]}" for key in sorted(params.keys()) if key in ["ctime", "type", "page", "count", "version"])
        return get_hmac512(path + get_hash256(param_string), config["SECRET_KEY"])

    def get_cookie():
        response = requests.get(config["URL"])
        return response.cookies.get_dict()

    def request_zing_mp3(path, params):
        cookies = get_cookie()
        response = requests.get(f"{config['URL']}{path}", params=params, cookies=cookies)
        return response.json()

    api_key = request.args.get("apikey")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")

    keyword = request.args.get("keyword", "")
    if not keyword:
        return jsonify({"error": "Yêu cầu từ khóa"}), 400

    try:
        ctime = str(int(time.time()))
        params = {
            "q": keyword,
            "type": config["TYPE"],
            "count": config["COUNT"],
            "ctime": ctime,
            "version": config["VERSION"],
            "apiKey": config["API_KEY"],
            "sig": get_sig(config["PATH"], {
                "q": keyword,
                "type": config["TYPE"],
                "count": config["COUNT"],
                "ctime": ctime,
                "version": config["VERSION"]
            })
        }
        result = request_zing_mp3(config["PATH"], params)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "status_code": 500}), 500

@app.route("/zingmp3_download", methods=["GET"])
def zingmp3_download():
    config = {
        "URL": "https://zingmp3.vn",
        "API_KEY": "X5BM3w8N7MKozC0B85o4KMlzLZKhV00y",
        "SECRET_KEY": "acOrvUS15XRW2o9JksiK1KgQ6Vbds8ZW",
        "VERSION": "1.11.11",
        "PATH": "/api/v2/song/get/streaming"
    }

    def get_hash256(string):
        return hashlib.sha256(string.encode()).hexdigest()

    def get_hmac512(string, key):
        return hmac.new(key.encode(), string.encode(), hashlib.sha512).hexdigest()

    def get_sig(path, params):
        param_string = ''.join(f"{key}={params[key]}" for key in sorted(params.keys()) if key in ["ctime", "id", "version"])
        return get_hmac512(path + get_hash256(param_string), config["SECRET_KEY"])

    def get_cookie():
        response = requests.get(config["URL"])
        return response.cookies.get_dict()

    def request_zing_mp3(path, params):
        cookies = get_cookie()
        response = requests.get(f"{config['URL']}{path}", params=params, cookies=cookies)
        return response.json()

    api_key = request.args.get("apikey")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")

    song_id = request.args.get("song_id", "")
    if not song_id:
        return jsonify({"error": "Yêu cầu ID bài hát"}), 400

    try:
        ctime = str(int(time.time()))
        params = {
            "id": song_id,
            "ctime": ctime,
            "version": config["VERSION"],
            "apiKey": config["API_KEY"],
            "sig": get_sig(config["PATH"], {
                "id": song_id,
                "ctime": ctime,
                "version": config["VERSION"]
            })
        }
        streaming_info = request_zing_mp3(config["PATH"], params)
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
    config = {
        "FILE_PATH": "assets/girl.txt"
    }

    def load_girl_images():
        try:
            with open(config["FILE_PATH"], 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            return []

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
    config = {
        "FILE_PATH": "assets/videogirl.txt"
    }

    def load_girl_videos():
        try:
            with open(config["FILE_PATH"], 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            return []

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
