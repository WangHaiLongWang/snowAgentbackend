1.在backend文件夹下,使用flask框架创建一个简单的后端项目.
2.将app.py文件中的代码 初始到/app相关文件中，包括__init__.py, models.py, views/main.py, config.py等等
3.在backend 文件夹下，1.我想通过蓝图和对应的路由构建相关api接口，帮我把项目中的蓝图和路由统一架构处理，2.我想去掉相关模板内容去掉render_template相关业务，3.初始化相关数据层业务内容保留相关db 端口和url 并且兼容一下初始化的api内容。
4.帮我梳理整个项目架构，以及形成mvc架构，去除冗余和重复的文件和文件夹，让系统的拓展性变强，增加可读能力
5.在当前app目录下，我想再区分开一些，比如
5.我想加入相关Agent业务内容，关于LLm初始化 以及从其他网站中拿取北大湖滑雪场相关天气数据 列如https://www.snow-forecast.com/resorts/Beidahu/6day/mid， 以及获取历史的北大湖相关雪场的 雪道开放计划，给我一些架构建议和应该怎么做

6 访问 https://www.snow-forecast.com/resorts/Beidahu/6day/mid ，将其内容总结一下，将当前天气内容能形成sqldb库表结构，在backend目录下，/app/task/文件夹下。 添加addWearch.py 文件，在此文件中编写相关任务的代码，以及能将内容，添加到对应的db数据库中。
7.在/app/task 文件夹下addWearch.py我进行了手动的修改与调整,在extract_forecast方法中获取到的forecast 数据为 ['-23', '-22', '-23', '-20', '-21', '-24', '-22', '-22', '-24', '-22', '-20', '-17', '-15', '-14', '-17', '-19', '-19', '-20'], 'temperatureMAX': None, 'weather': ['clear', 'clear', 'clear', 'clear', 'some clouds', 'some clouds', 'some clouds', 'light snow', 'light snow', 'some clouds', 'some clouds', 'some clouds', 'cloudy', 'cloudy', 'light snow', 'light snow', 'light snow', 'snow shwrs']， 需要在 extract_forecast方法中添加 时间维度按照数据来构成。时间 数据按照 一天分为AM PM night, 一天为三个数据，从当天的AM开始， 直到最后一天的night

8. 在/app/task 文件夹下addWearch.py我进行了手动的修改与调整， 在get_weather_data方法中forecast_data数据为[{'temperatureMin': ['-22', '-23', '-21', '-21', '-24', '-22', '-22', '-24', '-21', '-19', '-16', '-14', '-14', '-17', '-20', '-20', '-22'], 'temperatureMAX': None, 'weather': ['clear', 'clear', 'clear', 'clear', 'clear', 'cloudy', 'light snow', 'light snow', 'clear', 'clear', 'cloudy', 'cloudy', 'light snow', 'light snow', 'light snow', 'light snow', 'snow shwrs'], 'time': [{'week': 'Thu', 'month': '22'}, {'week': 'Friday', 'month': '23'}, {'week': 'Saturday', 'month': '24'}, {'week': 'Sunday', 'month': '25'}, {'week': 'Monday', 'month': '26'}, {'week': 'Tuesday', 'month': '27'}], 'timeSlot': ['AM', 'PM', 'night', 'AM', 'PM', 'night', 'AM', 'PM', 'night', 'AM', 'PM', 'night', 'AM', 'PM', 'night', 'AM', 'PM', 'night']}]。
current_weather_data数据为 [{'temperature': '-25', 'wind': '35', 'weather': 'clear'}, {'temperature': '-22', 'wind': '25', 'weather': 'clear'}, {'temperature': '-19', 'wind': '20', 'weather': 'cloud'}]，根据以上的数据帮我更新 save_weather_to_db 方法以及数据库表内容

9. 根据数据库雪场相关天气，对/app/control/routes.py文件中的雪场相关API进行更新，以及前端页面渲染相关字段进行更新