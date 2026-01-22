1.在backend文件夹下,使用flask框架创建一个简单的后端项目.
2.将app.py文件中的代码 初始到/app相关文件中，包括__init__.py, models.py, views/main.py, config.py等等
3.在backend 文件夹下，1.我想通过蓝图和对应的路由构建相关api接口，帮我把项目中的蓝图和路由统一架构处理，2.我想去掉相关模板内容去掉render_template相关业务，3.初始化相关数据层业务内容保留相关db 端口和url 并且兼容一下初始化的api内容。
4.帮我梳理整个项目架构，以及形成mvc架构，去除冗余和重复的文件和文件夹，让系统的拓展性变强，增加可读能力
5.在当前app目录下，我想再区分开一些，比如
5.我想加入相关Agent业务内容，关于LLm初始化 以及从其他网站中拿取北大湖滑雪场相关天气数据 列如https://www.snow-forecast.com/resorts/Beidahu/6day/mid， 以及获取历史的北大湖相关雪场的 雪道开放计划，给我一些架构建议和应该怎么做

6 访问 https://www.snow-forecast.com/resorts/Beidahu/6day/mid ，将其内容总结一下，将当前天气内容能形成sqldb库表结构，在backend目录下，/app/task/文件夹下。 添加addWearch.py 文件，在此文件中编写相关任务的代码，以及能将内容，添加到对应的db数据库中。