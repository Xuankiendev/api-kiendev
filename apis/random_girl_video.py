from flask import Blueprint, request, jsonify
import random
from ..app import validate_api_key, load_media

bp = Blueprint('random_girl_video', __name__)

@bp.route("/random_girl_video", methods=["GET"])
def random_girl_video():
    api_key = request.args.get("apikey")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation, ensure_ascii=False), mimetype="application/json")

    videos = load_media("assets/videogirl.txt")
    if not videos:
        return jsonify({"error": "Không có video nào trong danh sách"}, status=404)
    return jsonify({"video_url": random.choice(videos)})
