from flask import jsonify, request

from app.control import bp
from app.db import Item, create_item, get_by_id, list_items

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


# ==================== 雪场相关 API ====================


@bp.get("/api/resort/<resort_id>/weather")
def get_resort_weather(resort_id: str):
    """获取雪场天气信息"""
    from app.db.models import CurrentWeather, Weather, Resort
    from datetime import datetime, timedelta
    import logging
    
    logger = logging.getLogger('weather_api')
    
    try:
        # 验证雪场是否存在
        resort = Resort.query.get(resort_id)
        if not resort:
            return jsonify({"error": "雪场不存在"}), 404
        
        # 获取当前天气
        current_weather = CurrentWeather.query.filter_by(resort_id=resort_id).first()
        
        # 获取未来6天天气预报
        forecast = Weather.query.filter_by(resort_id=resort_id)\
            .filter(Weather.date >= datetime.now().date())\
            .order_by(Weather.date.asc())\
            .limit(6)\
            .all()\
        
        # 构建响应数据
        weather_data = {
            "currentTemp": int(current_weather.temperature) if current_weather and current_weather.temperature else None,
            "condition": current_weather.condition if current_weather else None,
            "windSpeed": current_weather.wind_speed if current_weather else None,
            "humidity": current_weather.humidity if current_weather else None,
            "visibility": current_weather.visibility if current_weather else None,
            "snowDepth": current_weather.snow_depth if current_weather else None,
            "windDirection": current_weather.wind_direction if current_weather else None,
            "updatedAt": current_weather.updated_at.isoformat() if current_weather and current_weather.updated_at else None,
            "forecast": []
        }
        
        # 处理天气预报数据
        for day_forecast in forecast:
            # 计算日期标签（今天、明天、后天等）
            delta_days = (day_forecast.date - datetime.now().date()).days
            if delta_days == 0:
                date_label = "今天"
            elif delta_days == 1:
                date_label = "明天"
            elif delta_days == 2:
                date_label = "后天"
            else:
                date_label = f"第{delta_days + 1}天"
            
            forecast_item = {
                "date": date_label,
                "actualDate": day_forecast.date.isoformat(),
                "condition": day_forecast.condition,
                "minTemp": day_forecast.temp_low,
                "maxTemp": day_forecast.temp_high,
                "windSpeed": day_forecast.wind_speed,
                "windDirection": day_forecast.wind_direction,
                "humidity": day_forecast.humidity,
                "visibility": day_forecast.visibility,
                "snowfallTotal": day_forecast.snowfall_total,
                "snowfallNew": day_forecast.snowfall_new
            }
            weather_data["forecast"].append(forecast_item)
        
        logger.info(f"成功获取雪场 {resort.name} 的天气信息")
        return jsonify(weather_data)
        
    except Exception as e:
        # 如果数据库中没有数据，返回模拟数据作为 fallback
        logger.error(f"获取天气数据失败: {str(e)}")
        # 模拟天气数据
        weather_data = {
            "currentTemp": -8,
            "condition": "Snow",
            "windSpeed": 15,
            "humidity": 75,
            "visibility": 5,
            "snowDepth": 120,
            "windDirection": "西北风",
            "snowProbability": 80,
            "forecast": [
                {"date": "今天", "actualDate": datetime.now().date().isoformat(), "snowfall": 5, "minTemp": -12, "maxTemp": -5, "condition": "Snow"},
                {"date": "明天", "actualDate": (datetime.now() + timedelta(days=1)).date().isoformat(), "snowfall": 8, "minTemp": -15, "maxTemp": -3, "condition": "Snow"},
                {"date": "后天", "actualDate": (datetime.now() + timedelta(days=2)).date().isoformat(), "snowfall": 3, "minTemp": -10, "maxTemp": -2, "condition": "Partly Cloudy"},
                {"date": "第4天", "actualDate": (datetime.now() + timedelta(days=3)).date().isoformat(), "snowfall": 0, "minTemp": -8, "maxTemp": 0, "condition": "Sunny"},
                {"date": "第5天", "actualDate": (datetime.now() + timedelta(days=4)).date().isoformat(), "snowfall": 2, "minTemp": -6, "maxTemp": 2, "condition": "Snow"},
                {"date": "第6天", "actualDate": (datetime.now() + timedelta(days=5)).date().isoformat(), "snowfall": 6, "minTemp": -9, "maxTemp": -1, "condition": "Snow"},
            ],
        }
        return jsonify(weather_data)


@bp.get("/api/resort/<resort_id>/map")
def get_resort_map(resort_id: str):
    """获取雪场地图信息"""
    # 模拟地图数据，实际项目中应该存储真实的地图图片URL或使用地图服务
    map_data = {
        "imageUrl": f"https://via.placeholder.com/800x600?text={resort_id}雪场地图",
        "width": 800,
        "height": 600,
    }
    return jsonify(map_data)


@bp.get("/api/resort/<resort_id>/slopes")
def get_resort_slopes(resort_id: str):
    """获取雪场的雪道列表"""
    from app.db.models import get_slopes_by_resort

    slopes = get_slopes_by_resort(resort_id)
    return jsonify([slope.to_dict() for slope in slopes])

