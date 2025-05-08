from flask import Blueprint, request
import requests
from .utils import check_key, json_response

tiktok_bp = Blueprint('tiktok', __name__)

@tiktok_bp.route('/tiktok_download', methods=['GET'])
def tiktok_download():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    tiktok_url = request.args.get('url', '')
    if not tiktok_url:
        return json_response({'error': 'Cần URL Video TikTok', 'status': 400}, 400)

    try:
        api_url = f'https://www.tikwm.com/api/?url={tiktok_url}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json'
        }
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return json_response({'error': 'Lỗi kết nối API TikTok', 'status': 500}, 500)

        data = response.json()
        if data.get('code', -1) != 0:
            return json_response({'error': 'URL Video TikTok sai', 'status': 400}, 400)
        if not data.get('data'):
            return json_response({'error': 'Không tìm thấy video', 'status': 404}, 404)
        return json_response(data)
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)
