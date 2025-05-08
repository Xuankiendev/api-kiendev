from flask import Blueprint, request
import requests
from .utils import check_key, json_response

check_ban_bp = Blueprint('check_ban', __name__)

@check_ban_bp.route('/check_ban', methods=['GET'])
def check_ban():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    uid = request.args.get('uid', '')
    if not uid:
        return json_response({'error': 'Cần UID người chơi', 'status': 400}, 400)

    config = {
        'url': f'https://ff.garena.com/api/antihack/check_banned?lang=en&uid={uid}',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'referer': 'https://ff.garena.com/en/support/',
            'x-requested-with': 'B6FksShzIgjfrYImLpTsadjS86sddhFH'
        }
    }
    try:
        response = requests.get(config['url'], headers=config['headers'], timeout=5)
        if response.status_code != 200:
            return json_response({'error': 'Không lấy được data', 'status': 500}, 500)

        data = response.json().get('data', {})
        is_banned = data.get('is_banned', 0)
        period = data.get('period', 0)
        return json_response({
            'credits': 'Vũ Xuân Kiên (@xkprj)',
            'telegram': 'https://t.me/sharecodevn',
            'status': 'Bị cấm' if is_banned else 'Không cấm',
            'ban_time': period if is_banned else 0,
            'uid': uid,
            'is_banned': bool(is_banned)
        })
    except Exception as e:
        return json_response({'error': f'Lỗi server: {str(e)}', 'status': 500}, 500)
