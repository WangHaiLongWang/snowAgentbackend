import cv2
import os
import tempfile
from datetime import datetime

class VideoProcessor:
    def __init__(self):
        pass
    
    def extract_frames(self, video_path, frame_interval=10, max_frames=50):
        """
        从视频中提取关键帧
        
        Args:
            video_path: 视频文件路径
            frame_interval: 帧间隔，每多少帧提取一次
            max_frames: 最大提取帧数
            
        Returns:
            frames: 提取的帧路径列表
        """
        frames = []
        
        # 打开视频文件
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise Exception(f"无法打开视频文件: {video_path}")
        
        # 获取视频基本信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 计算实际的帧间隔
        if total_frames > max_frames * frame_interval:
            frame_interval = total_frames // max_frames
        
        # 创建临时目录存储帧
        temp_dir = tempfile.mkdtemp()
        
        frame_count = 0
        extracted_count = 0
        
        while cap.isOpened() and extracted_count < max_frames:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # 每隔指定帧提取一次
            if frame_count % frame_interval == 0:
                # 生成帧文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                frame_filename = f"frame_{extracted_count}_{timestamp}.jpg"
                frame_path = os.path.join(temp_dir, frame_filename)
                
                # 保存帧
                cv2.imwrite(frame_path, frame)
                frames.append(frame_path)
                extracted_count += 1
            
            frame_count += 1
        
        # 释放视频捕获
        cap.release()
        
        return frames
    
    def cleanup_frames(self, frames):
        """
        清理临时帧文件
        
        Args:
            frames: 帧路径列表
        """
        for frame_path in frames:
            if os.path.exists(frame_path):
                try:
                    os.remove(frame_path)
                except:
                    pass
        
        # 清理临时目录
        if frames:
            temp_dir = os.path.dirname(frames[0])
            if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
                try:
                    os.rmdir(temp_dir)
                except:
                    pass
    
    def get_video_info(self, video_path):
        """
        获取视频信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            info: 视频信息字典
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise Exception(f"无法打开视频文件: {video_path}")
        
        info = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
        }
        
        cap.release()
        
        return info
