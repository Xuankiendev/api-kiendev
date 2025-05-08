from flask import Blueprint, request
import requests
import time
import hashlib
import hmac
from .utils import check_key, json_response

zingmp3_bp = Blueprint('zingmp3', __name__)

URL = "https://zingmp3.vn"
API_KEY = "X5BM3w8N7MKozC0B85o4KMlzLZKhV00y"
SECRET_KEY = "acOrvUS15XRW2o9JksiK1KgQ6Vbds8ZW"
VERSION = "1.11.11"

def get_hash256(string):
    return hashlib.sha256(string.encode()).hexdigest()

def get_hmac512(string, key):
    return hmac.new(key.encode(), string.encode(), hashlib.sha512).hexdigest()

def get_sig(path, params):
    param_string = ''.join(f"{key}={params[key]}" for key in sorted(params.keys()) if key in ["ctime", "id", "type", "page", "count", "version", "q"])
    return get_hmac512(path + get_hash256(param_string), SECRET_KEY)

def get_cookie():
    response = requests.get(URL)
    return response.cookies.get_dict()

def request_zing_mp3(path, params):
    cookies = get_cookie()
    response = requests.get(f"{URL}{path}", params=params, cookies=cookies)
    return response.json()

@zingmp3_bp.route('/zingmp3_search', methods=['GET'])
def zingmp3_search():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    keyword = request.args.get('keyword', '')
    if not keyword:
        return json_response({'error': 'Cần keyword để tìm kiếm', 'status': 400}, 400)

    try:
        ctime = str(int(time.time()))
        path = "/api/v2/search"
        params = {
            "q": keyword,
            "type": "song",
            "count": 10,
            "ctime": ctime,
            "version": VERSION,
            "apiKey": API_KEY,
        }
        params["sig"] = get_sig(path, params)
        data = request_zing_mp3(path, params)
        return json_response({'data': data})
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)

@zingmp3_bp.route('/zingmp3_download', methods=['GET'])
def zingmp3_download():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    song_id = request.args.get('song_id', '')
    if not song_id:
        return json_response({'error': 'Cần song_id để tải nhạc', 'status': 400}, 400)

    try:
        ctime = str(int(time.time()))
        path = "/api/v2/song/get/streaming"
        params = {
            "id": song_id,
            "ctime": ctime,
            "version": VERSION,
            "apiKey": API_KEY,
        }
        params["sig"] = get_sig(path, params)
        data = request_zing_mp3(path, params)
        return json_response({'data': data})
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)

@zingmp3_bp.route('/zingmp3_get_lyric', methods=['GET'])
def zingmp3_get_lyric():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    song_id = request.args.get('song_id', '')
    if not song_id:
        return json_response({'error': 'Cần song_id để lấy lời bài hát', 'status': 400}, 400)

    try:
        response = requests.get("https://m.zingmp3.vn/xhr/lyrics/get-lyrics", params={"media_id": song_id})
        data = response.json()
        return json_response({'data': data})
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)
