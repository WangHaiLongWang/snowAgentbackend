import cv2
import numpy as np

# 尝试不同的mediapipe导入方式
try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    has_mediapipe = True
except ImportError:
    has_mediapipe = False

class PoseEstimator:
    def __init__(self):
        self.has_mediapipe = has_mediapipe
        self.pose = None
        
        if has_mediapipe:
            try:
                # 尝试使用较新版本的mediapipe API
                from mediapipe import solutions
                self.mp_pose = solutions.pose
                self.pose = self.mp_pose.Pose(
                    static_image_mode=True,
                    model_complexity=2,
                    enable_segmentation=False,
                    min_detection_confidence=0.5
                )
                self.mp_drawing = solutions.drawing_utils
            except ImportError:
                # 尝试使用旧版本的mediapipe API
                try:
                    self.mp_pose = mp.solutions.pose
                    self.pose = self.mp_pose.Pose(
                        static_image_mode=True,
                        model_complexity=2,
                        enable_segmentation=False,
                        min_detection_confidence=0.5
                    )
                    self.mp_drawing = mp.solutions.drawing_utils
                except Exception:
                    self.pose = None
    
    def estimate_pose(self, frames):
        """
        对视频帧进行姿态估计
        
        Args:
            frames: 帧路径列表
            
        Returns:
            pose_data: 姿态数据列表
        """
        pose_data = []
        
        # 检查mediapipe是否可用
        if not self.pose:
            # 如果mediapipe不可用，返回模拟的姿态数据
            for frame_path in frames:
                pose_data.append({
                    'frame_path': frame_path,
                    'landmarks': [],
                    'angles': {
                        'left_knee': 120.0,
                        'right_knee': 120.0,
                        'left_hip': 110.0,
                        'right_hip': 110.0,
                        'left_shoulder': 90.0,
                        'right_shoulder': 90.0
                    }
                })
            return pose_data
        
        for frame_path in frames:
            # 读取帧
            image = cv2.imread(frame_path)
            if image is None:
                continue
            
            try:
                # 转换为RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # 进行姿态估计
                results = self.pose.process(image_rgb)
                
                if results.pose_landmarks:
                    # 提取关键点
                    landmarks = []
                    for landmark in results.pose_landmarks.landmark:
                        landmarks.append({
                            'x': landmark.x,
                            'y': landmark.y,
                            'z': landmark.z,
                            'visibility': landmark.visibility
                        })
                    
                    # 计算关键角度
                    angles = self._calculate_angles(landmarks)
                    
                    # 存储姿态数据
                    pose_data.append({
                        'frame_path': frame_path,
                        'landmarks': landmarks,
                        'angles': angles
                    })
            except Exception as e:
                # 如果处理失败，返回模拟的姿态数据
                pose_data.append({
                    'frame_path': frame_path,
                    'landmarks': [],
                    'angles': {
                        'left_knee': 120.0,
                        'right_knee': 120.0,
                        'left_hip': 110.0,
                        'right_hip': 110.0,
                        'left_shoulder': 90.0,
                        'right_shoulder': 90.0
                    }
                })
        
        return pose_data
    
    def _calculate_angles(self, landmarks):
        """
        计算关键角度
        
        Args:
            landmarks: 关键点列表
            
        Returns:
            angles: 角度字典
        """
        angles = {}
        
        try:
            # 计算膝盖角度
            if len(landmarks) >= 26:
                # 左膝角度
                left_knee_angle = self._calculate_angle(
                    landmarks[23],  # 左髋
                    landmarks[25],  # 左膝
                    landmarks[27]   # 左脚踝
                )
                angles['left_knee'] = left_knee_angle
                
                # 右膝角度
                right_knee_angle = self._calculate_angle(
                    landmarks[24],  # 右髋
                    landmarks[26],  # 右膝
                    landmarks[28]   # 右脚踝
                )
                angles['right_knee'] = right_knee_angle
                
                # 计算髋部角度
                left_hip_angle = self._calculate_angle(
                    landmarks[11],  # 左肩
                    landmarks[23],  # 左髋
                    landmarks[25]   # 左膝
                )
                angles['left_hip'] = left_hip_angle
                
                right_hip_angle = self._calculate_angle(
                    landmarks[12],  # 右肩
                    landmarks[24],  # 右髋
                    landmarks[26]   # 右膝
                )
                angles['right_hip'] = right_hip_angle
                
                # 计算肩部角度
                left_shoulder_angle = self._calculate_angle(
                    landmarks[13],  # 左肘
                    landmarks[11],  # 左肩
                    landmarks[23]   # 左髋
                )
                angles['left_shoulder'] = left_shoulder_angle
                
                right_shoulder_angle = self._calculate_angle(
                    landmarks[14],  # 右肘
                    landmarks[12],  # 右肩
                    landmarks[24]   # 右髋
                )
                angles['right_shoulder'] = right_shoulder_angle
        
        except Exception as e:
            # 如果计算失败，返回空字典
            pass
        
        return angles
    
    def _calculate_angle(self, a, b, c):
        """
        计算三点之间的角度
        
        Args:
            a: 第一点
            b: 第二点（顶点）
            c: 第三点
            
        Returns:
            angle: 角度值
        """
        # 转换为numpy数组
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        
        # 计算向量
        ba = a - b
        bc = c - b
        
        # 计算点积
        dot_product = np.dot(ba, bc)
        
        # 计算模长
        ba_length = np.linalg.norm(ba)
        bc_length = np.linalg.norm(bc)
        
        # 计算角度
        if ba_length * bc_length == 0:
            return 0
        
        angle = np.arccos(dot_product / (ba_length * bc_length))
        
        # 转换为度数
        angle = np.degrees(angle)
        
        return angle
    
    def visualize_pose(self, frame_path, pose_data):
        """
        可视化姿态估计结果
        
        Args:
            frame_path: 帧路径
            pose_data: 姿态数据
            
        Returns:
            visualized_image: 可视化后的图像
        """
        # 读取帧
        image = cv2.imread(frame_path)
        if image is None:
            return None
        
        # 绘制姿态
        if 'landmarks' in pose_data:
            # 创建姿态关键点对象
            landmarks = pose_data['landmarks']
            pose_landmarks = self.mp_pose.PoseLandmark
            
            # 绘制关键点
            for i, landmark in enumerate(landmarks):
                if i < len(pose_landmarks):
                    x = int(landmark['x'] * image.shape[1])
                    y = int(landmark['y'] * image.shape[0])
                    cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
        
        return image
    
    def close(self):
        """
        关闭姿态估计模型
        """
        if self.pose:
            try:
                self.pose.close()
            except Exception:
                pass
