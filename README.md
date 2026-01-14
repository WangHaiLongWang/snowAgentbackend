## 系统架构
myflaskapp/
│
├── app/                      # 应用包
│   ├── __init__.py          # 初始化文件，创建Flask应用实例
│   ├── models.py            # 数据库模型（如果使用数据库）
│   ├── views/               # 视图函数（或使用单个views.py文件，但更推荐使用蓝图分割）
│   │   ├── __init__.py
│   │   └── main.py          # 主视图
│   ├── static/              # 静态文件（CSS, JS, 图片等）
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/           # Jinja2模板
│   │   ├── base.html        # 基础模板
│   │   └── index.html       # 首页模板
│   └── config.py            # 配置文件
│
├── tests/                   # 测试文件
│   ├── __init__.py
│   └── test_basic.py
│
├── migrations/              # 数据库迁移脚本（如果使用Flask-Migrate）
│
├── venv/                    # 虚拟环境（通常不提交到版本控制）
│
├── requirements.txt         # 项目依赖
├── .gitignore              # Git忽略文件
├── run.py                  # 应用启动文件（可选，也可使用flask run）
└── README.md