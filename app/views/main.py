from flask import Blueprint, jsonify, request
from app.models import item_repo

# 创建蓝图
bp = Blueprint('main', __name__)

# 简单的健康检查路由
@bp.route('/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Flask Backend is running',
        'timestamp': request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    })

# 根路由
@bp.route('/')
def home():
    return jsonify({ 
        'message': 'Welcome to Flask Backend API',
        'endpoints': ['/health', '/api/data', '/api/data/<id>'],
        'method': request.method
    })

# GET请求示例 - 获取所有数据
@bp.route('/api/data', methods=['GET'])
def get_all_data():
    data = item_repo.get_all()
    return jsonify({
        'data': data,
        'count': len(data)
    })

# GET请求示例 - 根据ID获取单条数据
@bp.route('/api/data/<int:item_id>', methods=['GET'])
def get_data_by_id(item_id):
    item = item_repo.get_by_id(item_id)
    if item:
        return jsonify(item)
    return jsonify({'error': 'Item not found'}), 404

# POST请求示例 - 创建新数据
@bp.route('/api/data', methods=['POST'])
def create_data():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    data = request.get_json()
    if 'name' not in data or 'description' not in data:
        return jsonify({'error': 'Missing required fields: name, description'}), 400
    
    new_item = item_repo.create(data['name'], data['description'])
    return jsonify(new_item), 201

# 错误处理示例
@bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500