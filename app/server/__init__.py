from flask import Flask
from flasgger import Swagger

from app.server.config import config
from app.server.extensions import db


def create_app(config_name: str = "default") -> Flask:
    """Flask 应用工厂：统一在这里初始化扩展与注册蓝图。"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 初始化扩展（数据库等）
    db.init_app(app)

    # Swagger / OpenAPI 文档（访问：/apidocs/）
    Swagger(
        app,
        template={
            "swagger": "2.0",
            "info": {
                "title": "SnowAgent Backend API",
                "description": "Backend API documentation (Swagger UI).",
                "version": "1.0.0",
            },
        },
    )

    # 注册蓝图（统一 API，无模板渲染）
    from app.control import bp as api_bp

    app.register_blueprint(api_bp)

    # 轻量级初始化：自动建表 + 填充初始数据（如需更严谨建议引入 Flask-Migrate）
    with app.app_context():
        db.create_all()
        try:
            from app.db import seed_items_if_empty

            seed_items_if_empty()
        except Exception:
            # 避免启动因种子数据失败而中断（例如迁移阶段、表结构变化等）
            pass

    return app

