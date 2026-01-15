from flask import Blueprint

# 统一 API 蓝图入口（无模板渲染）
bp = Blueprint("api", __name__)

# 路由注册（延迟导入避免循环依赖）
from app.control import routes  # noqa: F401, E402

