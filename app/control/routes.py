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


