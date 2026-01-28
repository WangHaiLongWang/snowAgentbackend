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
    current_weatherData = []

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
                
            current_weatherData.append(current_weather)

    except Exception as e:
        print(f"提取当前天气失败: {str(e)}")
        
    print(f"提取当前天气成功: {str(current_weatherData)}")
    return current_weatherData

def extract_forecast(soup):
    """
    提取6天天气预报
    """
    forecast = []
    
    try:
        # 示例选择器，实际需要根据页面结构调整
        forecast_days = soup.find(class_='forecast-table__table')
        day_data = {
            'temperatureMin': None,
            'temperatureMAX': None,
            'weather': None,
            'time': None,
            'timeSlot': None
        }
        # 提取所有最低温度 
        temperatureMin_element = forecast_days.find('tr', attrs={'data-row': 'temperature-min'}).find_all(class_='forecast-table__cell')
        if temperatureMin_element:
            temperatureMinData = []
            for temperatureMinItem_element in temperatureMin_element:
                temperatureMinItemText = temperatureMinItem_element.find('div').text.strip()
                temperatureMinData.append(temperatureMinItemText)
            day_data['temperatureMin'] = temperatureMinData
            
        # 提取所有最高温度
        temperatureMax_element = forecast_days.find('tr', attrs={'data-row': 'temperature-max'}).find_all(class_='forecast-table__cell')
        if temperatureMax_element:
            temperatureMaxData = []
            for temperatureMaxItem_element in temperatureMax_element:
                temperatureMaxItemText = temperatureMaxItem_element.find('div').text.strip()
                temperatureMaxData.append(temperatureMaxItemText)
            day_data['temperatureMin'] = temperatureMaxData               
            
        # 温度
        weather_element = forecast_days.find('tr', attrs={'data-row': 'phrases'}).find_all(class_='forecast-table__cell')
        if weather_element:
            weatherData = []
            for weatherItem_element in weather_element:
                weatherText = weatherItem_element.find('span').text.strip()
                weatherData.append(weatherText)
            day_data['weather'] = weatherData               
        #时间 数据按照 一天分为AM PM night, 一天为三个数据，从当天的AM开始， 直到最后一天的night
        time_element = forecast_days.find_all(class_="forecast-table-days__content")
        if time_element:
            timeData = []
            timeSlotData = []
            timeSlot = ["AM", "PM", "night"]
            for timeItem_element in time_element:
                timeItemData = {
                    'week': None,
                    'month': None    
                }
                week_element = timeItem_element.find(class_='forecast-table-days__name').text.strip()
                month_element = timeItem_element.find(class_='forecast-table-days__date').text.strip()
                timeItemData['week'] = week_element
                timeItemData['month'] = month_element
                timeData.append(timeItemData)
                
                for timeSlotItem in timeSlot:
                    timeSlotData.append(timeSlotItem)
                
            day_data['time'] = timeData  
            day_data['timeSlot'] = timeSlotData  
        
        forecast.append(day_data)
        
    except Exception as e:
        print(f"提取天气预报失败: {str(e)}")
    
    return forecast

def save_weather_to_db(resort_id, current_weather, forecast_data):
    """
    将天气数据保存到数据库
    适配新的数据格式：
    - current_weather: 包含三个时间段数据的列表
    - forecast_data: 包含温度、天气、日期和时间段信息的字典
    """
    # 保存当前天气（使用第一个时间段的数据）
    if current_weather and isinstance(current_weather, list) and len(current_weather) > 0:
        current_data = current_weather[0]  # 使用第一个时间段的数据作为当前天气
        
        # 检查是否已存在当前天气记录
        existing_current = CurrentWeather.query.filter_by(resort_id=resort_id).first()
        
        if existing_current:
            # 更新现有记录
            existing_current.temperature = int(current_data.get('temperature', 0)) if current_data.get('temperature') else None
            existing_current.condition = current_data.get('weather', '')
            existing_current.wind_speed = int(current_data.get('wind', 0)) if current_data.get('wind') else None
            existing_current.updated_at = datetime.now()
        else:
            # 创建新记录
            new_current_weather = CurrentWeather(
                resort_id=resort_id,
                temperature=int(current_data.get('temperature', 0)) if current_data.get('temperature') else None,
                condition=current_data.get('weather', ''),
                wind_speed=int(current_data.get('wind', 0)) if current_data.get('wind') else None
            )
            db.session.add(new_current_weather)
    
    # 保存天气预报
    if forecast_data and isinstance(forecast_data, list) and len(forecast_data) > 0:
        forecast = forecast_data[0]  # 获取第一个元素，包含所有预报信息
        
        # 提取预报数据
        temperatures = forecast.get('temperatureMin', [])
        weathers = forecast.get('weather', [])
        dates = forecast.get('time', [])
        time_slots = forecast.get('timeSlot', [])
        
        # 确保数据长度一致（每天3个时间段，6天）
        data_length = min(len(temperatures), len(weathers), len(time_slots))
        dates_length = len(dates)
        
        # 按天处理数据（6天）
        for day_index in range(min(6, dates_length)):
            # 计算日期
            year = datetime.now().year
            month = datetime.now().month
            day = int(dates[day_index]['month'])
            
            # 处理跨月情况
            try:
                forecast_date = datetime(year, month, day).date()
            except ValueError:
                # 如果日期无效，使用当前日期加上偏移
                forecast_date = (datetime.now() + timedelta(days=day_index)).date()
            
            # 提取当天的三个时间段数据
            day_temperatures = []
            day_weathers = []
            
            for period_index in range(3):
                data_index = day_index * 3 + period_index
                if data_index < data_length:
                    # 收集温度数据（用于计算最高/最低温度）
                    temp_str = temperatures[data_index]
                    if temp_str and temp_str != '-':
                        try:
                            day_temperatures.append(int(temp_str))
                        except ValueError:
                            pass
                    
                    # 收集天气数据
                    day_weathers.append(weathers[data_index])
            
            # 计算当天的最高和最低温度
            temp_low = min(day_temperatures) if day_temperatures else None
            temp_high = max(day_temperatures) if day_temperatures else None
            
            # 确定当天的主要天气状况（出现最频繁的）
            main_weather = ''
            if day_weathers:
                from collections import Counter
                weather_counter = Counter(day_weathers)
                main_weather = weather_counter.most_common(1)[0][0]
            
            # 检查是否已存在该日期的记录
            existing_forecast = Weather.query.filter_by(
                resort_id=resort_id,
                date=forecast_date
            ).first()
            
            if existing_forecast:
                # 更新现有记录
                existing_forecast.condition = main_weather
                existing_forecast.temp_high = temp_high
                existing_forecast.temp_low = temp_low
                existing_forecast.updated_at = datetime.now()
            else:
                # 创建新记录
                new_forecast = Weather(
                    resort_id=resort_id,
                    date=forecast_date,
                    condition=main_weather,
                    temp_high=temp_high,
                    temp_low=temp_low
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