from flask import Flask, request, jsonify, Response
import hashlib
import hmac
import time
import requests
import json

app = Flask(__name__)

with open('config.json', 'r') as f:
    config = json.load(f)
    VALID_API_KEYS = {
        config['apikey']: "active"
    }

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
        return {"err": -1, "msg": "Failed to fetch lyrics"}

def validate_api_key(api_key):
    if not api_key:
        return {"error": "API key is missing", "status_code": 401}
    if api_key not in VALID_API_KEYS:
        return {"error": "Invalid API key", "status_code": 401}
    
    status = VALID_API_KEYS[api_key]
    if status == "inactive":
        return {"error": "API key is changed", "status_code": 403}
    if status == "banned":
        return {"error": "API key is banned", "status_code": 403}
    
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
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json().get("data", {})
            is_banned = data.get("is_banned", 0)
            period = data.get("period", 0)
            result = {
                "credits": "Vũ Xuân Kiên (@xkprj)",
                "groupTelegram": "https://t.me/sharecodevn",
                "status": "BANNED" if is_banned else "NOT BANNED",
                "banPeriod": period if is_banned else 0,
                "uid": player_id,
                "isBanned": bool(is_banned)
            }
            return Response(json.dumps(result), mimetype="application/json")
        else:
            return Response(json.dumps({"error": "Failed to fetch data from server", "status_code": 500}), mimetype="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e), "status_code": 500}), mimetype="application/json")

@app.route("/check_ban", methods=["GET"])
def bancheck():
    api_key = request.args.get("apikey")
    if not api_key:
        return Response(json.dumps({"error": "API key is missing", "status_code": 401}), mimetype="application/json")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")
    player_id = request.args.get("uid", "")
    if not player_id:
        return Response(json.dumps({"error": "Player ID is required", "status_code": 400}), mimetype="application/json")
    return check_banned(player_id)

@app.route("/zingmp3_search", methods=["GET"])
def zingmp3_search():
    api_key = request.args.get("apikey")
    if not api_key:
        return Response(json.dumps({"error": "API key is missing", "status_code": 401}), mimetype="application/json")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")
    keyword = request.args.get("keyword", "")
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400
    result = search_music(keyword)
    return jsonify(result)

@app.route("/zingmp3_download", methods=["GET"])
def zingmp3_download():
    api_key = request.args.get("apikey")
    if not api_key:
        return Response(json.dumps({"error": "API key is missing", "status_code": 401}), mimetype="application/json")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")
    song_id = request.args.get("song_id", "")
    if not song_id:
        return jsonify({"error": "Song ID is required"}), 400
    streaming_info = get_streaming_song(song_id)
    if "data" in streaming_info:
        download_url = streaming_info["data"].get("streaming", "")
        if download_url:
            return jsonify({"download_url": download_url})
        else:
            return jsonify({"error": "Download URL not found"}), 404
    else:
        return jsonify({"error": "Failed to get song streaming data"}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": [
            "Liên hệ:",
            "Telegram: Vũ Xuân Kiên (@xkprj)",
            "Group Telegram: @deptraiaiyeu",
            "Để lấy cách sử dụng APIs!"
        ]
    })

if __name__ == "__main__":
    app.run(debug=True)
