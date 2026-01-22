import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.server.extensions import db
from app.db.models import Weather, CurrentWeather, Resort

def get_weather_data(resort_id, resort_name):
    """
    从snow-forecast.com获取指定雪场的天气数据
    """
    # 雪场名称到URL名称的映射
    resort_url_map = {
        '北大湖': 'Beidahu',
        '松花湖': 'SonghuaLake',
        '可可托海': 'Koktokay'
    }
    
    # 获取正确的URL名称
    resort_url_name = resort_url_map.get(resort_name, resort_name)
    url = f"https://www.snow-forecast.com/resorts/{resort_url_name}/6day/mid"
    
    try:
        # 发送请求获取页面内容
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析页面内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        
        # 提取当前天气信息
        current_weather_data = extract_current_weather(soup)
        
        print(f"提取当前天气信息{current_weather_data}")
        
        # 提取6天天气预报
        forecast_data = extract_forecast(soup)
        
        print(f"6天天气预报{forecast_data}")
        
        # 保存到数据库
        save_weather_to_db(resort_id, current_weather_data, forecast_data)
        
        print(f"成功获取并保存{resort_name}的天气数据")
        return True
        
    except Exception as e:
        print(f"获取天气数据失败: {str(e)}")
        return False

def extract_current_weather(soup):
    """
    提取当前天气信息
    """
    current_weather = []

    try:
        
        # 示例选择器，实际需要根据页面结构调整
        temp_element = soup.find_all(class_='live-snow__table-row') 

        for temp in temp_element:
            # 这里需要根据实际页面结构调整选择器
            current_weather = {
                'temperature': None,
                'wind': None,
                'weather': None,
            }
            # 温度
            temperatureTop_element = temp.find(class_="live-snow__table-temperature")
            if temperatureTop_element:
                current_weather['temperature'] = temperatureTop_element.text.strip()
            
            # 风
            wind_element = temp.find(class_="live-snow__table-cell--wind").find(class_="wind-icon__val")
            if wind_element:
                current_weather['wind'] = wind_element.text.strip()
                        
            # 天气
            weather_element = temp.find(class_="live-snow__table-cell--weather").find(class_="weather-icon")
            if weather_element:
                current_weather['weather'] = weather_element.get('alt', '')
                
            current_weather.append(current_weather)

    except Exception as e:
        print(f"提取当前天气失败: {str(e)}")
        
    print(f"提取当前天气成功: {str(current_weather)}")
    return current_weather

def extract_forecast(soup):
    """
    提取6天天气预报
    """
    forecast = []
    
    try:
        # 示例选择器，实际需要根据页面结构调整
        forecast_days = soup.find_all(class_='forecast-table__table')
        
        for day in forecast_days:
            day_data = {
                'temperatureMin': None,
                'temperatureMAX': None,
                'weather': None,
            }
            # 提取所有最低温度 
            temperatureMin_element = day.find('div', attrs={'data-row': 'temperature-min'}).find_all(class_='forecast-table__cell')
            if temperatureMin_element:
                temperatureMinData = []
                for temperatureMinItem_element in temperatureMin_element:
                    temperatureMinItemText = temperatureMinItem_element.find('div').text.strip()
                    temperatureMinData.append(temperatureMinItemText)
                day_data['temperatureMin'] = temperatureMinData
                
            # 提取所有最高温度
            temperatureMax_element = day.find('div', attrs={'data-row': 'temperature-max'}).find_all(class_='forecast-table__cell')
            if temperatureMax_element:
                temperatureMaxData = []
                for temperatureMaxItem_element in temperatureMax_element:
                    temperatureMaxItemText = temperatureMaxItem_element.find('div').text.strip()
                    temperatureMaxData.append(temperatureMaxItemText)
                day_data['temperatureMin'] = temperatureMaxData               
                
            # 温度
            weather_element = day.find('div', attrs={'data-row': 'phrases'}).find_all(class_='forecast-table__cell')
            if weather_element:
                weatherData = []
                for weatherItem_element in weather_element:
                    weatherText = weatherItem_element.find('span').text.strip()
                    weatherData.append(weatherText)
                day_data['weather'] = weatherData               
            #时间 数据按照 一天分为AM PM night, 一天为三个数据，从当天的AM开始， 直到最后一天的night
        
            forecast.append(day_data)
        
    except Exception as e:
        print(f"提取天气预报失败: {str(e)}")
    
    return forecast

def save_weather_to_db(resort_id, current_weather, forecast_data):
    """
    将天气数据保存到数据库
    """
    # 保存当前天气
    if current_weather:
        # 检查是否已存在当前天气记录
        existing_current = CurrentWeather.query.filter_by(resort_id=resort_id).first()
        
        if existing_current:
            # 更新现有记录
            existing_current.temperature = current_weather.get('temperature')
            existing_current.condition = current_weather.get('condition')
            existing_current.wind_speed = current_weather.get('wind_speed')
            existing_current.wind_direction = current_weather.get('wind_direction')
            existing_current.visibility = current_weather.get('visibility')
            existing_current.humidity = current_weather.get('humidity')
            existing_current.snow_depth = current_weather.get('snow_depth')
            existing_current.updated_at = datetime.now()
        else:
            # 创建新记录
            new_current_weather = CurrentWeather(
                resort_id=resort_id,
                temperature=current_weather.get('temperature'),
                condition=current_weather.get('condition'),
                wind_speed=current_weather.get('wind_speed'),
                wind_direction=current_weather.get('wind_direction'),
                visibility=current_weather.get('visibility'),
                humidity=current_weather.get('humidity'),
                snow_depth=current_weather.get('snow_depth')
            )
            db.session.add(new_current_weather)
    
    # 保存天气预报
    for forecast in forecast_data:
        if forecast.get('date'):
            # 检查是否已存在该日期的记录
            existing_forecast = Weather.query.filter_by(
                resort_id=resort_id,
                date=forecast['date']
            ).first()
            
            if existing_forecast:
                # 更新现有记录
                existing_forecast.condition = forecast.get('condition')
                existing_forecast.temp_high = forecast.get('temp_high')
                existing_forecast.temp_low = forecast.get('temp_low')
                existing_forecast.snowfall_total = forecast.get('snowfall_total')
                existing_forecast.snowfall_new = forecast.get('snowfall_new')
                existing_forecast.wind_speed = forecast.get('wind_speed')
                existing_forecast.wind_direction = forecast.get('wind_direction')
                existing_forecast.visibility = forecast.get('visibility')
                existing_forecast.humidity = forecast.get('humidity')
                existing_forecast.updated_at = datetime.now()
            else:
                # 创建新记录
                new_forecast = Weather(
                    resort_id=resort_id,
                    date=forecast['date'],
                    condition=forecast.get('condition'),
                    temp_high=forecast.get('temp_high'),
                    temp_low=forecast.get('temp_low'),
                    snowfall_total=forecast.get('snowfall_total'),
                    snowfall_new=forecast.get('snowfall_new'),
                    wind_speed=forecast.get('wind_speed'),
                    wind_direction=forecast.get('wind_direction'),
                    visibility=forecast.get('visibility'),
                    humidity=forecast.get('humidity')
                )
                db.session.add(new_forecast)
    
    # 提交事务
    db.session.commit()

def main():
    """
    主函数，执行天气数据获取任务
    """
    # 从数据库获取所有雪场
    resorts = Resort.query.all()
    
    for resort in resorts:
        print(f"正在获取{resort.name}的天气数据...")
        get_weather_data(resort.id, resort.name)
    
    print("所有雪场天气数据获取完成")

if __name__ == "__main__":
    from app.server import create_app
    
    # 创建Flask应用上下文
    app = create_app()
    with app.app_context():
        main()