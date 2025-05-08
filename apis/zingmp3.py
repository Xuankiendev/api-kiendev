from flask import Blueprint, request
import requests
import hashlib
import hmac
import time
from .utils import check_key, json_response

zingmp3_bp = Blueprint('zingmp3', __name__)

CONFIG = {
    'url': 'https://zingmp3.vn',
    'api_key': 'X5BM3w8N7MKozC0B85o4KMlzLZKhV00y',
    'secret_key': 'acOrvUS15XRW2o9JksiK1KgQ6Vbds8ZW',
    'version': '1.11.11',
    'search_path': '/api/v2/search',
    'download_path': '/api/v2/song/get/streaming',
    'count': 10,
    'type': 'song'
}

def hash256(string):
    return hashlib.sha256(string.encode()).hexdigest()

def hmac512(string, key):
    return hmac.new(key.encode(), string.encode(), hashlib.sha512).hexdigest()

def get_cookie():
    try:
        return requests.get(CONFIG['url'], timeout=5).cookies.get_dict()
    except Exception:
        return {}

def zing_request(path, params):
    try:
        response = requests.get(f"{CONFIG['url']}{path}", params=params, cookies=get_cookie(), timeout=5)
        return response.json()
    except Exception:
        return {'error': 'Lỗi API', 'status': 500}

@zingmp3_bp.route('/zingmp3_search', methods=['GET'])
def zingmp3_search():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    keyword = request.args.get('keyword', '')
    if not keyword:
        return json_response({'error': 'Cần từ khóa', 'status': 400}, 400)

    try:
        ctime = str(int(time.time()))
        params = {
            'q': keyword,
            'type': CONFIG['type'],
            'count': CONFIG['count'],
            'ctime': ctime,
            'version': CONFIG['version'],
            'apiKey': CONFIG['api_key'],
            'sig': hmac512(CONFIG['search_path'] + hash256(f"count={CONFIG['count']}ctime={ctime}type={CONFIG['type']}version={CONFIG['version']}"), CONFIG['secret_key'])
        }
        return json_response(zing_request(CONFIG['search_path'], params))
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)

@zingmp3_bp.route('/zingmp3_download', methods=['GET'])
def zingmp3_download():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    song_id = request.args.get('song_id', '')
    if not song_id:
        return json_response({'error': 'Cần ID bài hát', 'status': 400}, 400)

    try:
        ctime = str(int(time.time()))
        params = {
            'id': song_id,
            'ctime': ctime,
            'version': CONFIG['version'],
            'apiKey': CONFIG['api_key'],
            'sig': hmac512(CONFIG['download_path'] + hash256(f"ctime={ctime}id={song_id}version={CONFIG['version']}"), CONFIG['secret_key'])
        }
        data = zing_request(CONFIG['download_path'], params)
        if data.get('err', -1) != 0 or not data.get('data'):
            return json_response({'error': 'Không tải được bài hát', 'status': 500}, 500)

        audio_url = data['data'].get('320')
        quality = '320kbps'
        if audio_url == 'VIP' or not audio_url:
            audio_url = data['data'].get('128')
            quality = '128kbps'

        if not audio_url:
            return json_response({'error': 'Không tìm thấy link tải', 'status': 404}, 404)
        return json_response({'download_url': audio_url, 'quality': quality})
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)
