from flask import Blueprint, request, jsonify
import hashlib
import hmac
import time
import requests
from ..app import validate_api_key

bp = Blueprint('zingmp3_download', __name__)

@bp.route("/zingmp3_download", methods=["GET"])
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
        return Response(json.dumps(key_validation, ensure_ascii=False), mimetype="application/json")

    song_id = request.args.get("song_id", "")
    if not song_id:
        return jsonify({"error": "Yêu cầu ID bài hát"}, status=400)

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
        
        if streaming_info.get("err", -1) != 0 or not streaming_info.get("data"):
            return jsonify({"error": "Không thể tải bài hát này", "status_code": 500}, status=500)
        
        audio_url = streaming_info["data"].get("320")
        quality = "320kbps"
        if audio_url == "VIP" or not audio_url:
            audio_url = streaming_info["data"].get("128")
            quality = "128kbps"
        
        if not audio_url:
            return jsonify({"error": "Không tìm thấy URL tải xuống", "status_code": 404}, status=404)
        
        return jsonify({
            "download_url": audio_url,
            "quality": quality
        })
    except Exception as e:
        return jsonify({"error": str(e), "status_code": 500}, status=500)
