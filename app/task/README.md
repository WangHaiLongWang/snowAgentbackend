# 雪场天气数据更新模块

## 功能介绍

本模块用于自动获取雪场的天气数据，并将其保存到数据库中。支持以下功能：

- 从OpenWeatherMap API获取雪场天气数据
- 每天4次自动更新天气数据
- 为无法获取数据的雪场提供默认天气数据
- 支持4个雪场：北大湖、松花湖、可可托海、禾木

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 直接运行weather_updater.py

```bash
# 只运行一次更新
python app/task/weather_updater.py --once

# 启动自动更新调度器
python app/task/weather_updater.py
```

### 2. 使用入口脚本

```bash
# 只运行一次更新
python run_weather_updater.py --once

# 启动自动更新调度器
python run_weather_updater.py
```

### 3. 在服务器中作为服务运行

#### Linux系统（使用systemd）

创建服务文件 `/etc/systemd/system/weather-updater.service`：

```ini
[Unit]
Description=雪场天气数据更新服务
After=network.target

[Service]
User=your-username
WorkingDirectory=/path/to/snowagent/backend
ExecStart=/path/to/python run_weather_updater.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable weather-updater.service
sudo systemctl start weather-updater.service
```

#### Windows系统（使用任务计划程序）

1. 打开任务计划程序
2. 创建新任务
3. 设置触发器为每天的6:00、12:00、18:00、00:00
4. 设置操作为运行以下命令：
   ```
   python.exe /path/to/snowagent/backend/run_weather_updater.py --once
   ```

## 配置说明

### OpenWeatherMap API密钥

API密钥已在代码中硬编码为 `004d182648179f8a0ea148f56c0840ea`，如果需要更换，请修改 `weather_updater.py` 文件中的 `self.owm_api_key` 值。

### 雪场配置

雪场的经纬度信息已在代码中配置，位于 `weather_updater.py` 文件中的 `self.resort_info_map` 字典。如果需要修改或添加雪场，请更新此字典。

## 日志

日志文件位于 `app/task/weather_updater.log`，记录了天气数据更新的详细信息。

## API接口

更新后的天气数据可以通过以下API接口获取：

- 北大湖：`http://127.0.0.1:5000/api/resort/beidahu/weather`
- 松花湖：`http://127.0.0.1:5000/api/resort/songhuahu/weather`
- 可可托海：`http://127.0.0.1:5000/api/resort/koktokay/weather`
- 禾木：`http://127.0.0.1:5000/api/resort/hemu/weather`
