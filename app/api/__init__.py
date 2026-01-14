from flask import Blueprint

# 统一 API 蓝图入口（无模板渲染）
bp = Blueprint("api", __name__)

# 路由注册
from app.api import routes as _routes  # noqa: F401

