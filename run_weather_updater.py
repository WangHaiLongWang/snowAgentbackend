#!/usr/bin/env python3
"""
雪场天气数据更新工具入口脚本

此脚本用于在系统和服务器中调用weather_updater.py

用法:
    # 只运行一次更新
    python run_weather_updater.py --once
    
    # 启动自动更新调度器
    python run_weather_updater.py
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.task.weather_updater import WeatherUpdater

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="雪场天气数据更新工具")
    parser.add_argument("--once", action="store_true", help="只运行一次更新，不启动调度器")
    args = parser.parse_args()
    
    updater = WeatherUpdater()
    
    if args.once:
        # 只运行一次更新
        updater.update_all_resorts()
        print("天气数据更新完成，退出程序")
    else:
        # 运行调度器
        updater.run_scheduler()
