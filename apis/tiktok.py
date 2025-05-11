from flask import Blueprint, request, Response
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
        return json_response({'error': 'Cần URL TikTok', 'status': 400}, 400)

    try:
        api_url = f'https://www.tikwm.com/api/?url={tiktok_url}'
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            return json_response({'error': 'Lỗi kết nối API TikTok', 'status': 500}, 500)

        data = response.json()
        if data.get('code', -1) != 0:
            return json_response({'error': 'URL TikTok sai', 'status': 400}, 400)
        if not data.get('data'):
            return json_response({'error': 'Không tìm thấy video', 'status': 404}, 404)
        return json_response(data)
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)

@tiktok_bp.route('/get_posts', methods=['GET'])
def get_posts():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    unique_id = request.args.get('unique_id', '')
    if not unique_id:
        return json_response({'error': 'Cần unique_id', 'status': 400}, 400)

    try:
        api_url = f'https://www.tikwm.com/api/user/posts?unique_id={unique_id}'
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            return json_response({'error': 'Lỗi kết nối API TikTok', 'status': 500}, 500)

        data = response.json()
        if data.get('code', -1) != 0:
            return json_response({'error': 'unique_id không hợp lệ', 'status': 400}, 400)
        if not data.get('data'):
            return json_response({'error': 'Không tìm thấy bài đăng', 'status': 404}, 404)
        return json_response(data)
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)

@tiktok_bp.route('/search_tiktok', methods=['GET'])
def search():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    keywords = request.args.get('keywords', '')
    if not keywords:
        return json_response({'error': 'Cần từ khóa tìm kiếm', 'status': 400}, 400)

    try:
        api_url = f'https://www.tikwm.com/api/feed/search?keywords={keywords}'
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            return json_response({'error': 'Lỗi kết nối API TikTok', 'status': 500}, 500)

        data = response.json()
        if data.get('code', -1) != 0:
            return json_response({'error': 'Từ khóa không hợp lệ', 'status': 400}, 400)
        if not data.get('data'):
            return json_response({'error': 'Không tìm thấy kết quả', 'status': 404}, 404)
        return json_response(data)
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)

@tiktok_bp.route('/tiktok_user_info', methods=['GET'])
def tiktok_user_info():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    unique_id = request.args.get('unique_id', '')
    if not unique_id:
        return json_response({'error': 'Cần unique_id', 'status': 400}, 400)

    try:
        api_url = f'https://www.tikwm.com/api/user/info?unique_id={unique_id}'
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            return json_response({'error': 'Lỗi kết nối API TikTok', 'status': 500}, 500)

        data = response.json()
        if data.get('code', -1) != 0:
            return json_response({'error': 'unique_id không hợp lệ', 'status': 400}, 400)
        if not data.get('data'):
            return json_response({'error': 'Không tìm thấy thông tin người dùng', 'status': 404}, 404)
        return json_response(data)
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)
