from flask import Blueprint, request, redirect
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

    screenshot_url = f'https://api.site-shot.com/?url={url}&userkey=MAAIEYKBJAOPKB7IQ6LBIZ2BT3'
    return redirect(screenshot_url)
