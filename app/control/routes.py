from flask import jsonify, request

from app.control import bp
from app.db import Item, create_item, get_by_id, list_items


@bp.get("/health")
def health_check():
    return jsonify(
        {
            "status": "ok",
            "message": "Flask Backend is running",
            "client_ip": request.environ.get("HTTP_X_REAL_IP", request.remote_addr),
        }
    )


@bp.get("/")
def home():
    return jsonify(
        {
            "message": "Welcome to Flask Backend API",
            "endpoints": ["/health", "/api/data", "/api/data/<id>"],
            "method": request.method,
        }
    )


@bp.get("/api/data")
def get_all_data():
    data = [item.to_dict() for item in list_items()]
    return jsonify({"data": data, "count": len(data)})


@bp.get("/api/data/<int:item_id>")
def get_data_by_id(item_id: int):
    item = get_by_id(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item.to_dict())


@bp.post("/api/data")
def create_data():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    description = data.get("description")
    if not name or not description:
        return jsonify({"error": "Missing required fields: name, description"}), 400

    item: Item = create_item(name=name, description=description)
    return jsonify(item.to_dict()), 201


@bp.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Not found"}), 404


@bp.errorhandler(500)
def internal_error(_error):
    return jsonify({"error": "Internal server error"}), 500


