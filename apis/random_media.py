from flask import Blueprint, request
import random
from .utils import check_key, json_response

random_media_bp = Blueprint('random_media', __name__)

def load_media(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        return []

@random_media_bp.route('/random_girl_image', methods=['GET'])
def random_girl_image():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    images = load_media('assets/girl.txt')
    if not images:
        return json_response({'error': 'Không có ảnh', 'status': 404}, 404)
    return json_response({'image_url': random.choice(images)})

@random_media_bp.route('/random_girl_video', methods=['GET'])
def random_girl_video():
    api_key = request.args.get('apikey')
    if error := check_key(api_key):
        return json_response(error, error['status'])

    videos = load_media('assets/videogirl.txt')
    if not videos:
        return json_response({'error': 'Không có video', 'status': 404}, 404)
    return json_response({'video_url': random.choice(videos)})
