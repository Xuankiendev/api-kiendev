from flask import Blueprint, request, Response
import requests
from .utils import check_key, json_response

screenshot_bp = Blueprint('screenshot', __name__)

@screenshot_bp.route('/screenshot', methods=['GET'])
def screenshot():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    url = request.args.get('url', '')
    if not url:
        return json_response({'error': 'Cần URL để chụp ảnh', 'status': 400}, 400)

    try:
        screenshot_url = f'https://api.site-shot.com/?url={url}&userkey=MAAIEYKBJAOPKB7IQ6LBIZ2BT3'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/*'
        }
        response = requests.get(screenshot_url, headers=headers, timeout=15)
        if response.status_code != 200:
            return json_response({
                'error': 'Không chụp được ảnh',
                'status_code': response.status_code,
                'response_text': response.text[:200]
            }, 500)
        return Response(response.content, mimetype=response.headers.get('Content-Type', 'image/png'))
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)
