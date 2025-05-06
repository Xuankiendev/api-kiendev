from flask import Blueprint, request, jsonify
import hashlib
import hmac
import time
import requests
from ..app import validate_api_key

bp = Blueprint('zingmp3_search', __name__)

@bp.route("/zingmp3_search", methods=["GET"])
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
        return Response(json.dumps(key_validation, ensure_ascii=False), mimetype="application/json")

    keyword = request.args.get("keyword", "")
    if not keyword:
        return jsonify({"error": "Yêu cầu tên bài hát"}, status=400)

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
        return jsonify({"error": str(e), "status_code": 500}, status=500)
