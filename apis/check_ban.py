from flask import Blueprint, request, Response
import requests
import json
from ..app import validate_api_key

bp = Blueprint('check_ban', __name__)

@bp.route("/check_ban", methods=["GET"])
def bancheck():
    def check_banned(player_id):
        config = {
            "url": f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "referer": "https://ff.garena.com/en/support/",
                "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"
            }
        }
        try:
            response = requests.get(config["url"], headers=config["headers"], timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                is_banned = data.get("is_banned", 0)
                period = data.get("period", 0)
                result = {
                    "credits": "Vũ Xuân Kiên (@xkprj)",
                    "groupTelegram": "https://t.me/sharecodevn",
                    "status": "Bị cấm" if is_banned else "Không bị cấm",
                    "banPeriod": period if is_banned else 0,
                    "uid": player_id,
                    "isBanned": bool(is_banned)
                }
                return Response(json.dumps(result, ensure_ascii=False), mimetype="application/json")
            else:
                return Response(json.dumps({"error": "Không thể lấy dữ liệu từ máy chủ", "status_code": 500}, ensure_ascii=False), mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e), "status_code": 500}, ensure_ascii=False), mimetype="application/json")

    api_key = request.args.get("apikey")
    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation, ensure_ascii=False), mimetype="application/json")
    
    player_id = request.args.get("uid", "")
    if not player_id:
        return Response(json.dumps({"error": "Yêu cầu ID người chơi", "status_code": 400}, ensure_ascii=False), mimetype="application/json")
    
    return check_banned(player_id)
