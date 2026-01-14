from flask import Flask
from app.config import Config, config

# 创建应用工厂函数
def create_app(config_name='default'):
    app = Flask(__name__)
    # 从配置类加载配置
    app.config.from_object(config[config_name])

    # 初始化扩展（例如，数据库、邮件等）
    # db.init_app(app)
    
    # 注册蓝图
    from app.views.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app