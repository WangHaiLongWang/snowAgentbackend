import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import sys
import schedule
import time
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.server.extensions import db
from app.db.models import Weather, CurrentWeather, Resort

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(__file__), 'weather_updater.log')
)
logger = logging.getLogger('weather_updater')

class WeatherUpdater:
    def __init__(self):
        # 雪场信息映射，包含经纬度和名称
        self.resort_info_map = {
            '北大湖': {'name': 'Beidahu', 'lat': 43.46072402, 'lon': 126.616401},
            '松花湖': {'name': 'SonghuaLake', 'lat': 43.694810, 'lon': 126.633613},
            '可可托海': {'name': 'Koktokay', 'lat': 47.211545, 'lon': 90.05280},
            '禾木': {'name': 'Hemu', 'lat': 48.5492354, 'lon': 87.5470512}
        }
        
        # OpenWeatherMap API配置
        self.owm_api_key = '004d182648179f8a0ea148f56c0840ea'
        self.owm_base_url = 'https://api.openweathermap.org/data/2.5'
        
        # 初始化数据库会话
        from app.server import create_app
        self.app = create_app()
    
    def get_weather_data(self, resort_id, resort_name):
        """
        从OpenWeatherMap API获取指定雪场的天气数据
        """
        try:
            # 获取雪场的经纬度信息
            resort_info = self.resort_info_map.get(resort_name)
            if not resort_info:
                logger.error(f"未找到{resort_name}的经纬度信息")
                # 为该雪场保存默认数据
                self.save_weather_to_db(resort_id, None, None)
                logger.info(f"为{resort_name}保存默认天气数据")
                return False
            
            lat = resort_info['lat']
            lon = resort_info['lon']
            
            # 获取当前天气数据
            current_weather_data = self.get_current_weather(lat, lon)
            
            # 获取5天天气预报数据
            forecast_data = self.get_forecast_weather(lat, lon)

            # 保存到数据库
            self.save_weather_to_db(resort_id, current_weather_data, forecast_data)
            
            logger.info(f"成功获取并保存{resort_name}的天气数据")
            return True
            
        except Exception as e:
            logger.error(f"获取{resort_name}天气数据失败: {str(e)}")
            # 即使获取失败，也为该雪场保存默认数据
            self.save_weather_to_db(resort_id, None, None)
            logger.info(f"为{resort_name}保存默认天气数据")
            return False
    
    def get_current_weather(self, lat, lon):
        """
        从OpenWeatherMap API获取当前天气数据
        """
        try:
            # 构建API URL
            url = f"{self.owm_base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.owm_api_key,
                'units': 'metric',
                'lang': 'zh_cn'
            }
            
            # 发送请求
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # 解析响应数据
            data = response.json()
            
            # 提取当前天气信息
            current_weather = {
                'temperature': int(data['main']['temp']),
                'wind_speed': int(data['wind']['speed'] * 3.6),  # 转换为km/h
                'condition': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'visibility': int(data.get('visibility', 10000) / 1000),  # 转换为km
                'wind_direction': self.degrees_to_direction(data['wind'].get('deg', 0)),
                'snow_depth': data.get('snow', {}).get('1h', 0) if 'snow' in data else 0
            }
            
            return current_weather
            
        except Exception as e:
            logger.error(f"获取当前天气数据失败: {str(e)}")
            return None
    
    def get_forecast_weather(self, lat, lon):
        """
        从OpenWeatherMap API获取5天天气预报数据
        """
        try:
            # 构建API URL
            url = f"{self.owm_base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.owm_api_key,
                'units': 'metric',
                'lang': 'zh_cn'
            }
            
            # 发送请求
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # 解析响应数据
            data = response.json()
            
            # 按天整理预报数据
            daily_forecasts = {}
            
            for item in data['list']:
                # 提取日期
                forecast_date = datetime.fromtimestamp(item['dt']).date()
                
                if forecast_date not in daily_forecasts:
                    daily_forecasts[forecast_date] = {
                        'temp_high': item['main']['temp_max'],
                        'temp_low': item['main']['temp_min'],
                        'conditions': [item['weather'][0]['description']],
                        'wind_speed': item['wind']['speed'] * 3.6,  # 转换为km/h
                        'humidity': item['main']['humidity'],
                        'snowfall': item.get('snow', {}).get('3h', 0) if 'snow' in item else 0
                    }
                else:
                    # 更新最高/最低温度
                    if item['main']['temp_max'] > daily_forecasts[forecast_date]['temp_high']:
                        daily_forecasts[forecast_date]['temp_high'] = item['main']['temp_max']
                    if item['main']['temp_min'] < daily_forecasts[forecast_date]['temp_low']:
                        daily_forecasts[forecast_date]['temp_low'] = item['main']['temp_min']
                    
                    # 添加天气状况
                    daily_forecasts[forecast_date]['conditions'].append(item['weather'][0]['description'])
                    
                    # 更新降雪量
                    daily_forecasts[forecast_date]['snowfall'] += item.get('snow', {}).get('3h', 0) if 'snow' in item else 0
            
            # 构建预报数据列表
            forecast = []
            for forecast_date, data in sorted(daily_forecasts.items()):
                # 确定当天的主要天气状况
                from collections import Counter
                condition_counter = Counter(data['conditions'])
                main_condition = condition_counter.most_common(1)[0][0]
                
                forecast_item = {
                    'date': forecast_date,
                    'temp_high': int(data['temp_high']),
                    'temp_low': int(data['temp_low']),
                    'condition': main_condition,
                    'wind_speed': int(data['wind_speed']),
                    'humidity': data['humidity'],
                    'snowfall': data['snowfall']
                }
                forecast.append(forecast_item)
            
            return forecast
            
        except Exception as e:
            logger.error(f"获取天气预报数据失败: {str(e)}")
            return []
    
    def degrees_to_direction(self, degrees):
        """
        将风向角度转换为方向
        """
        directions = ['北风', '东北风', '东风', '东南风', '南风', '西南风', '西风', '西北风']
        index = round(degrees / 45) % 8
        return directions[index]
    
    def save_weather_to_db(self, resort_id, current_weather, forecast_data):
        """
        将天气数据保存到数据库
        """
        with self.app.app_context():
            try:
                # 为无法获取数据的雪场提供默认数据
                if not current_weather:
                    current_weather = {
                        'temperature': -10,
                        'wind_speed': 10,
                        'condition': 'Snow',
                        'humidity': 70,
                        'visibility': 5,
                        'wind_direction': '北风',
                        'snow_depth': 0
                    }
                
                # 保存当前天气
                # 检查是否已存在当前天气记录
                existing_current = CurrentWeather.query.filter_by(resort_id=resort_id).first()
                
                if existing_current:
                    # 更新现有记录
                    existing_current.temperature = current_weather.get('temperature')
                    existing_current.condition = current_weather.get('condition')
                    existing_current.wind_speed = current_weather.get('wind_speed')
                    existing_current.humidity = current_weather.get('humidity')
                    existing_current.visibility = current_weather.get('visibility')
                    existing_current.wind_direction = current_weather.get('wind_direction')
                    existing_current.snow_depth = current_weather.get('snow_depth')
                    existing_current.updated_at = datetime.now()
                else:
                    # 创建新记录
                    new_current_weather = CurrentWeather(
                        resort_id=resort_id,
                        temperature=current_weather.get('temperature'),
                        condition=current_weather.get('condition'),
                        wind_speed=current_weather.get('wind_speed'),
                        humidity=current_weather.get('humidity'),
                        visibility=current_weather.get('visibility'),
                        wind_direction=current_weather.get('wind_direction'),
                        snow_depth=current_weather.get('snow_depth')
                    )
                    db.session.add(new_current_weather)
                
                # 为无法获取数据的雪场生成默认预报数据
                if not forecast_data:
                    forecast_data = []
                    for i in range(6):
                        forecast_date = (datetime.now() + timedelta(days=i)).date()
                        forecast_data.append({
                            'date': forecast_date,
                            'temp_low': -15 + i,
                            'temp_high': -5 + i,
                            'condition': 'Snow',
                            'wind_speed': 10,
                            'humidity': 70,
                            'snowfall': 0
                        })
                
                # 保存天气预报
                for forecast_day in forecast_data:
                    # 获取预报日期
                    forecast_date = forecast_day.get('date')
                    if not forecast_date:
                        continue
                    
                    # 检查是否已存在该日期的记录
                    existing_forecast = Weather.query.filter_by(
                        resort_id=resort_id,
                        date=forecast_date
                    ).first()
                    
                    if existing_forecast:
                        # 更新现有记录
                        existing_forecast.condition = forecast_day.get('condition')
                        existing_forecast.temp_high = forecast_day.get('temp_high')
                        existing_forecast.temp_low = forecast_day.get('temp_low')
                        existing_forecast.wind_speed = forecast_day.get('wind_speed')
                        existing_forecast.humidity = forecast_day.get('humidity')
                        existing_forecast.snowfall_new = forecast_day.get('snowfall')
                        existing_forecast.updated_at = datetime.now()
                    else:
                        # 创建新记录
                        new_forecast = Weather(
                            resort_id=resort_id,
                            date=forecast_date,
                            condition=forecast_day.get('condition'),
                            temp_high=forecast_day.get('temp_high'),
                            temp_low=forecast_day.get('temp_low'),
                            wind_speed=forecast_day.get('wind_speed'),
                            humidity=forecast_day.get('humidity'),
                            snowfall_new=forecast_day.get('snowfall')
                        )
                        db.session.add(new_forecast)
                
                # 提交事务
                db.session.commit()
                logger.info(f"成功保存天气数据到数据库")
                
            except Exception as e:
                logger.error(f"保存天气数据到数据库失败: {str(e)}")
                db.session.rollback()
    
    def update_all_resorts(self):
        """
        更新所有雪场的天气数据
        """
        with self.app.app_context():
            # 从数据库获取所有雪场
            resorts = Resort.query.all()
            
            # 确保数据库中有所有4个雪场的记录
            expected_resorts = {
                "beidahu": "北大湖",
                "songhuahu": "松花湖",
                "koktokay": "可可托海",
                "hemu": "禾木"
            }
            
            # 检查并添加缺失的雪场
            for resort_id, resort_name in expected_resorts.items():
                existing_resort = Resort.query.get(resort_id)
                if not existing_resort:
                    new_resort = Resort(id=resort_id, name=resort_name)
                    db.session.add(new_resort)
                    logger.info(f"添加新雪场: {resort_name}")
            
            # 如果有添加新雪场，提交事务
            if db.session.new:
                db.session.commit()
                # 重新获取所有雪场
                resorts = Resort.query.all()
            
            # 如果仍然没有雪场，使用默认数据
            if not resorts:
                default_resorts = [
                    Resort(id="beidahu", name="北大湖"),
                    Resort(id="songhuahu", name="松花湖"),
                    Resort(id="koktokay", name="可可托海"),
                    Resort(id="hemu", name="禾木")
                ]
                db.session.add_all(default_resorts)
                db.session.commit()
                resorts = default_resorts
            
            for resort in resorts:
                logger.info(f"正在获取{resort.name}的天气数据...")
                self.get_weather_data(resort.id, resort.name)
            
            logger.info("所有雪场天气数据更新完成")
    
    def run_scheduler(self):
        """
        运行调度器，每天4次自动更新天气数据
        """
        # 每天更新的时间点
        update_times = ["06:00", "12:00", "18:00", "00:00"]
        
        # 设置定时任务
        for update_time in update_times:
            schedule.every().day.at(update_time).do(self.update_all_resorts)
        
        logger.info("天气数据更新调度器已启动，每天4次自动更新")
        
        # 立即执行一次更新
        self.update_all_resorts()
        
        # 运行调度器
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="雪场天气数据更新工具")
    parser.add_argument("--once", action="store_true", help="只运行一次更新，不启动调度器")
    args = parser.parse_args()
    
    updater = WeatherUpdater()
    
    if args.once:
        # 只运行一次更新
        updater.update_all_resorts()
        logger.info("天气数据更新完成，退出程序")
    else:
        # 运行调度器
        updater.run_scheduler()
