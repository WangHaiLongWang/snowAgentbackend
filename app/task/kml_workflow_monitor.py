#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KML文件处理工作流监控器
监控KML文件上传并自动触发处理流程
"""

import os
import time
import threading
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('KMLWorkflowMonitor')

class KMLFileHandler(FileSystemEventHandler):
    """KML文件事件处理器"""
    
    def __init__(self, workflow_config):
        self.workflow_config = workflow_config
        self.processing_files = set()
    
    def on_created(self, event):
        """处理文件创建事件"""
        if not event.is_directory and event.src_path.endswith('.kml'):
            logger.info(f"检测到新的KML文件: {event.src_path}")
            self.process_kml_file(event.src_path)
    
    def on_modified(self, event):
        """处理文件修改事件"""
        if not event.is_directory and event.src_path.endswith('.kml'):
            # 避免重复处理
            if event.src_path not in self.processing_files:
                logger.info(f"检测到KML文件修改: {event.src_path}")
                self.process_kml_file(event.src_path)
    
    def process_kml_file(self, file_path):
        """处理KML文件"""
        try:
            # 添加到处理中集合，避免重复处理
            self.processing_files.add(file_path)
            
            logger.info(f"开始处理KML文件: {file_path}")
            
            # 运行KML处理脚本
            script_path = self.workflow_config['steps'][0]['config']['script_path']
            working_dir = self.workflow_config['steps'][0]['config']['working_directory']
            
            logger.info(f"运行脚本: {script_path}")
            
            # 执行脚本
            result = subprocess.run(
                ['python', script_path],
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            # 记录输出
            if result.returncode == 0:
                logger.info(f"KML文件处理成功: {file_path}")
                logger.info(f"脚本输出: {result.stdout}")
            else:
                logger.error(f"KML文件处理失败: {file_path}")
                logger.error(f"错误输出: {result.stderr}")
            
            # 验证处理结果
            self.verify_result(file_path)
            
        except Exception as e:
            logger.error(f"处理KML文件时出错: {str(e)}")
        finally:
            # 从处理中集合移除
            if file_path in self.processing_files:
                self.processing_files.remove(file_path)
    
    def verify_result(self, input_file):
        """验证处理结果"""
        try:
            # 生成预期的输出文件名
            base_name = os.path.basename(input_file)
            if '1.0.0' in base_name:
                expected_output = base_name.replace('1.0.0', '1.0.1')
                expected_path = os.path.join(os.path.dirname(input_file), expected_output)
                
                if os.path.exists(expected_path):
                    logger.info(f"验证成功: 处理后的文件已生成: {expected_path}")
                else:
                    logger.warning(f"验证失败: 处理后的文件未生成: {expected_path}")
            else:
                logger.info(f"跳过验证: 文件不是1.0.0版本: {input_file}")
                
        except Exception as e:
            logger.error(f"验证处理结果时出错: {str(e)}")

def load_workflow_config(config_path):
    """加载工作流配置"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载工作流配置时出错: {str(e)}")
        raise

def start_monitor(config):
    """启动监控器"""
    # 获取监控目录
    monitor_dir = config['trigger']['config']['directory']
    
    logger.info(f"启动KML文件监控器，监控目录: {monitor_dir}")
    
    # 创建事件处理器
    event_handler = KMLFileHandler(config)
    
    # 创建观察者
    observer = Observer()
    observer.schedule(event_handler, monitor_dir, recursive=False)
    
    # 启动观察者
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("KML文件监控器已停止")
    
    observer.join()

def main():
    """主函数"""
    # 加载工作流配置
    config_path = os.path.join(os.path.dirname(__file__), 'kml_workflow.yaml')
    config = load_workflow_config(config_path)
    
    # 启动监控器
    start_monitor(config)

if __name__ == "__main__":
    main()
