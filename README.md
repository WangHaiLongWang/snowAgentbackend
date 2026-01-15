## 系统架构

本项目采用清晰的三层架构：**server**（服务器层）、**control**（控制层）、**db**（数据层）。

```
backend/
│
├── app/                      # 应用包
│   ├── __init__.py          # 对外导出 create_app（保持向后兼容）
│   │
│   ├── server/               # 服务器层：应用配置、扩展初始化
│   │   ├── __init__.py      # 应用工厂函数 create_app()
│   │   ├── config.py        # 配置类（开发/测试/生产环境）
│   │   └── extensions.py    # 第三方扩展统一管理（db, redis 等）
│   │
│   ├── control/             # 控制层：路由和请求处理
│   │   ├── __init__.py      # 创建 API 蓝图
│   │   └── routes.py        # 路由定义和请求处理逻辑
│   │
│   ├── db/                  # 数据层：数据库模型和操作
│   │   ├── __init__.py      # 导出模型和 CRUD 函数
│   │   └── models.py        # SQLAlchemy 模型定义和数据库操作
│   │
│   └── services/            # 业务逻辑层（预留，用于复杂业务逻辑）
│
├── instance/                # 数据库文件存放目录（Flask 标准位置）
│   └── app.db              # SQLite 数据库文件
│
├── tests/                   # 测试文件
│
├── requirements.txt         # 项目依赖
├── run.py                  # 应用启动文件
└── README.md               # 本文件
```

## 架构说明

### 1. Server 层（`app/server/`）
- **职责**：应用初始化、配置管理、扩展注册
- **`__init__.py`**：Flask 应用工厂函数，初始化数据库、注册蓝图
- **`config.py`**：环境配置（开发/测试/生产），数据库连接、邮件等配置
- **`extensions.py`**：统一管理 Flask 扩展（SQLAlchemy、Redis 等），避免循环导入

### 2. Control 层（`app/control/`）
- **职责**：HTTP 请求处理、路由定义、参数验证、响应格式化
- **`__init__.py`**：创建 API 蓝图
- **`routes.py`**：定义所有 API 路由，处理请求并返回 JSON 响应

### 3. DB 层（`app/db/`）
- **职责**：数据库模型定义、CRUD 操作、数据访问逻辑
- **`__init__.py`**：统一导出模型类和操作函数
- **`models.py`**：SQLAlchemy 模型定义、查询函数、种子数据初始化

## 使用方式

### 启动应用
```bash
cd backend
python run.py
```

### 访问 API
- 健康检查：`GET http://localhost:5000/health`
- API 首页：`GET http://localhost:5000/`
- 获取所有数据：`GET http://localhost:5000/api/data`
- 根据 ID 获取：`GET http://localhost:5000/api/data/<id>`
- 创建数据：`POST http://localhost:5000/api/data`

## 扩展指南

### 添加新的数据模型
1. 在 `app/db/models.py` 中定义新的 SQLAlchemy 模型
2. 在 `app/db/__init__.py` 中导出新模型和操作函数
3. 在 `app/control/routes.py` 中添加对应的路由

### 添加新的业务逻辑
1. 在 `app/services/` 中创建服务模块（如 `weather_service.py`）
2. 在 `app/control/routes.py` 中调用服务层函数

### 添加新的配置项
1. 在 `app/server/config.py` 的 `Config` 类中添加配置项
2. 可通过环境变量覆盖（使用 `.env` 文件）

## 技术栈

- Flask 2.3.2
- Flask-SQLAlchemy 3.0.5
- python-dotenv 1.0.0
