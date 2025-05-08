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
        screenshot_url = f'https://api.site-shot.com/?url={url}&userkey=MAAIEYKBJAIDBB7IYJLBPSC6LV'
        response = requests.get(screenshot_url, timeout=10)
        if response.status_code != 200:
            return json_response({'error': 'Không chụp được ảnh', 'status': 500}, 500)
        return Response(response.content, mimetype=response.headers['Content-Type'])
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)
