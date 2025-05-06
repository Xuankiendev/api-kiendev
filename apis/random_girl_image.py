from flask import Blueprint, request, jsonify
import random
from ..app import validate_api_key, load_media

bp = Blueprint('random_girl_image', __name__)

@bp.route("/random_girl_image", methods=["GET"])
def random_girl_image():
    api_key = request.args.get("apikey")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation, ensure_ascii=False), mimetype="application/json")

    images = load_media("assets/girl.txt")
    if not images:
        return jsonify({"error": "Không có ảnh nào trong danh sách"}, status=404)
    return jsonify({"image_url": random.choice(images)})
