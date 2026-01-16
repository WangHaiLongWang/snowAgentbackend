from flask import jsonify, request

from app.control import bp
from app.db import Item, create_item, get_by_id, list_items


@bp.get("/health")
def health_check():
    """
    健康检查
    ---
    tags:
      - system
    responses:
      200:
        description: ok
    """
    return jsonify(
        {
            "status": "ok",
            "message": "Flask Backend is running",
            "client_ip": request.environ.get("HTTP_X_REAL_IP", request.remote_addr),
        }
    )


@bp.get("/")
def home():
    """
    API 首页
    ---
    tags:
      - system
    responses:
      200:
        description: API information
    """
    return jsonify(
        {
            "message": "Welcome to Flask Backend API",
            "endpoints": ["/health", "/api/data", "/api/data/<id>"],
            "method": request.method,
        }
    )


@bp.get("/api/data")
def get_all_data():
    """
    获取所有 Item
    ---
    tags:
      - items
    responses:
      200:
        description: Item list
    """
    data = [item.to_dict() for item in list_items()]
    return jsonify({"data": data, "count": len(data)})


@bp.get("/api/data/<int:item_id>")
def get_data_by_id(item_id: int):
    """
    根据 ID 获取 Item
    ---
    tags:
      - items
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Item
      404:
        description: Not found
    """
    item = get_by_id(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item.to_dict())


@bp.post("/api/data")
def create_data():
    """
    创建 Item
    ---
    tags:
      - items
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - description
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      201:
        description: Created
      400:
        description: Bad request
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    description = data.get("description")
    if not name or not description:
        return jsonify({"error": "Missing required fields: name, description"}), 400

    item: Item = create_item(name=name, description=description)
    return jsonify(item.to_dict()), 201


@bp.get("/debug/routes")
def debug_routes():
    """
    展示已注册的蓝图和路由（调试用）
    ---
    tags:
      - debug
    responses:
      200:
        description: blueprints and routes
    """
    from flask import current_app

    rules = []
    for rule in current_app.url_map.iter_rules():
        methods = sorted([m for m in rule.methods if m not in {"HEAD", "OPTIONS"}])
        rules.append(
            {
                "endpoint": rule.endpoint,
                "methods": methods,
                "rule": str(rule),
            }
        )

    blueprints = sorted(list(current_app.blueprints.keys()))
    return jsonify({"blueprints": blueprints, "routes": sorted(rules, key=lambda r: r["rule"])})


@bp.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Not found"}), 404


@bp.errorhandler(500)
def internal_error(_error):
    return jsonify({"error": "Internal server error"}), 500


# ==================== 雪场相关 API ====================


@bp.get("/api/resort/<resort_id>/weather")
def get_resort_weather(resort_id: str):
    """获取雪场天气信息（模拟数据，实际应从外部API获取）"""
    # 模拟天气数据，实际项目中应该从 snow-forecast.com 或其他天气API获取
    weather_data = {
        "currentTemp": -8,
        "condition": "Snow",
        "windSpeed": 15,
        "humidity": 75,
        "visibility": 5,
        "snowProbability": 80,
        "forecast": [
            {"date": "今天", "snowfall": 5, "minTemp": -12, "maxTemp": -5},
            {"date": "明天", "snowfall": 8, "minTemp": -15, "maxTemp": -3},
            {"date": "后天", "snowfall": 3, "minTemp": -10, "maxTemp": -2},
            {"date": "第4天", "snowfall": 0, "minTemp": -8, "maxTemp": 0},
            {"date": "第5天", "snowfall": 2, "minTemp": -6, "maxTemp": 2},
            {"date": "第6天", "snowfall": 6, "minTemp": -9, "maxTemp": -1},
        ],
    }
    return jsonify(weather_data)


@bp.get("/api/resort/<resort_id>/map")
def get_resort_map(resort_id: str):
    """获取雪场地图信息"""
    # 模拟地图数据，实际项目中应该存储真实的地图图片URL或使用地图服务
    map_data = {
        "imageUrl": f"https://via.placeholder.com/800x600?text={resort_id}雪场地图",
        "width": 800,
        "height": 600,
    }
    return jsonify(map_data)


@bp.get("/api/resort/<resort_id>/slopes")
def get_resort_slopes(resort_id: str):
    """获取雪场的雪道列表"""
    from app.db.models import get_slopes_by_resort

    slopes = get_slopes_by_resort(resort_id)
    return jsonify([slope.to_dict() for slope in slopes])

