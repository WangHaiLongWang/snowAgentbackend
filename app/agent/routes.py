from flask import Blueprint, jsonify, request, current_app
import os
import uuid
from datetime import datetime

from app.agent.video_processor import VideoProcessor
from app.agent.pose_estimator import PoseEstimator
from app.agent.model_evaluator import ModelEvaluator
from app.agent.agent_memory import AgentMemory
from app.agent.chat_manager import ChatManager

# 创建蓝图
bp = Blueprint('agent', __name__, url_prefix='/api/agent')

# 初始化各个模块
video_processor = VideoProcessor()
pose_estimator = PoseEstimator()
model_evaluator = ModelEvaluator()
agent_memory = AgentMemory()
chat_manager = ChatManager(agent_memory)


@bp.route('/video/upload', methods=['POST'])
def upload_video():
    """
    上传视频文件
    ---
    tags:
      - agent
    consumes:
      - multipart/form-data
    parameters:
      - name: video
        in: formData
        type: file
        required: true
        description: 滑雪视频文件
      - name: ski_type
        in: formData
        type: string
        required: true
        description: 滑雪类型（单板/双板）
      - name: skill_level
        in: formData
        type: string
        required: true
        description: 技能水平（初级/中级/高级）
    responses:
      200:
        description: 上传成功
        schema:
          type: object
          properties:
            task_id:
              type: string
              description: 任务ID
            message:
              type: string
              description: 上传成功消息
    """
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        ski_type = request.form.get('ski_type', '双板')
        skill_level = request.form.get('skill_level', '中级')
        
        if video_file.filename == '':
            return jsonify({'error': 'No video file selected'}), 400
        
        # 生成唯一的任务ID
        task_id = str(uuid.uuid4())
        
        # 确保上传目录存在
        upload_dir = os.path.join(current_app.root_path, '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存视频文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{task_id}_{timestamp}_{video_file.filename}"
        filepath = os.path.join(upload_dir, filename)
        video_file.save(filepath)
        
        # 保存任务信息
        task_info = {
            'task_id': task_id,
            'filepath': filepath,
            'ski_type': ski_type,
            'skill_level': skill_level,
            'status': 'uploaded',
            'created_at': datetime.now().isoformat()
        }
        
        # 存储任务信息（这里使用内存存储，实际项目中应该使用数据库）
        if not hasattr(current_app, 'video_tasks'):
            current_app.video_tasks = {}
        current_app.video_tasks[task_id] = task_info
        
        return jsonify({
            'task_id': task_id,
            'message': 'Video uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/video/status/<task_id>', methods=['GET'])
def get_video_status(task_id):
    """
    获取视频处理状态
    ---
    tags:
      - agent
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
        description: 任务ID
    responses:
      200:
        description: 状态信息
        schema:
          type: object
          properties:
            task_id:
              type: string
            status:
              type: string
            message:
              type: string
    """
    try:
        if not hasattr(current_app, 'video_tasks') or task_id not in current_app.video_tasks:
            return jsonify({'error': 'Task not found'}), 404
        
        task_info = current_app.video_tasks[task_id]
        return jsonify({
            'task_id': task_id,
            'status': task_info.get('status', 'unknown'),
            'message': task_info.get('message', '')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/analysis/process/<task_id>', methods=['POST'])
def process_video(task_id):
    """
    处理视频并分析
    ---
    tags:
      - agent
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
        description: 任务ID
    responses:
      200:
        description: 分析任务已启动
        schema:
          type: object
          properties:
            task_id:
              type: string
            message:
              type: string
    """
    try:
        if not hasattr(current_app, 'video_tasks') or task_id not in current_app.video_tasks:
            return jsonify({'error': 'Task not found'}), 404
        
        task_info = current_app.video_tasks[task_id]
        task_info['status'] = 'processing'
        task_info['message'] = '视频分析中...'
        
        # 异步处理视频（这里简化处理，实际项目中应该使用任务队列）
        def process_task():
            try:
                # 1. 视频抽帧
                frames = video_processor.extract_frames(task_info['filepath'])
                task_info['frames'] = frames
                task_info['status'] = 'extracting_frames'
                task_info['message'] = '正在提取视频帧...'
                
                # 2. 姿态估计
                pose_data = pose_estimator.estimate_pose(frames)
                task_info['pose_data'] = pose_data
                task_info['status'] = 'estimating_pose'
                task_info['message'] = '正在分析姿态...'
                
                # 3. 模型评价
                evaluation = model_evaluator.evaluate(frames, pose_data, task_info['ski_type'], task_info['skill_level'])
                task_info['evaluation'] = evaluation
                task_info['status'] = 'completed'
                task_info['message'] = '分析完成'
                
            except Exception as e:
                task_info['status'] = 'error'
                task_info['message'] = f'分析失败: {str(e)}'
        
        # 启动处理（这里使用同步处理，实际项目中应该使用异步）
        process_task()
        
        return jsonify({
            'task_id': task_id,
            'message': 'Video analysis started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/analysis/result/<task_id>', methods=['GET'])
def get_analysis_result(task_id):
    """
    获取分析结果
    ---
    tags:
      - agent
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
        description: 任务ID
    responses:
      200:
        description: 分析结果
        schema:
          type: object
          properties:
            task_id:
              type: string
            status:
              type: string
            evaluation:
              type: object
    """
    try:
        if not hasattr(current_app, 'video_tasks') or task_id not in current_app.video_tasks:
            return jsonify({'error': 'Task not found'}), 404
        
        task_info = current_app.video_tasks[task_id]
        
        if task_info['status'] != 'completed':
            return jsonify({
                'task_id': task_id,
                'status': task_info['status'],
                'message': task_info['message']
            })
        
        return jsonify({
            'task_id': task_id,
            'status': task_info['status'],
            'evaluation': task_info.get('evaluation', {})
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/chat/message', methods=['POST'])
def send_chat_message():
    """
    发送聊天消息
    ---
    tags:
      - agent
    parameters:
      - name: message
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              description: 聊天消息
            user_id:
              type: string
              description: 用户ID
    responses:
      200:
        description: 聊天响应
        schema:
          type: object
          properties:
            response:
              type: string
              description: 聊天响应
            conversation_id:
              type: string
              description: 对话ID
    """
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'default')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # 处理聊天消息
        response = chat_manager.handle_message(message, user_id)
        
        return jsonify({
            'response': response,
            'conversation_id': user_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/chat/history/<user_id>', methods=['GET'])
def get_chat_history(user_id):
    """
    获取聊天历史
    ---
    tags:
      - agent
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: 用户ID
    responses:
      200:
        description: 聊天历史
        schema:
          type: object
          properties:
            history:
              type: array
              items:
                type: object
                properties:
                  role:
                    type: string
                  content:
                    type: string
    """
    try:
        history = agent_memory.get_history(user_id)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/chat/clear/<user_id>', methods=['POST'])
def clear_chat_history(user_id):
    """
    清空聊天历史
    ---
    tags:
      - agent
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
        description: 用户ID
    responses:
      200:
        description: 清空成功
        schema:
          type: object
          properties:
            message:
              type: string
              description: 清空成功消息
    """
    try:
        agent_memory.clear_history(user_id)
        return jsonify({'message': 'Chat history cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/plan/generate', methods=['POST'])
def generate_plan():
    """
    生成学习计划
    ---
    tags:
      - agent
    parameters:
      - name: plan
        in: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: string
              description: 用户ID
            ski_type:
              type: string
              description: 滑雪类型（单板/双板）
            skill_level:
              type: string
              description: 当前技能水平
            goals:
              type: string
              description: 学习目标
    responses:
      200:
        description: 学习计划
        schema:
          type: object
          properties:
            plan:
              type: string
              description: 学习计划
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default')
        ski_type = data.get('ski_type', '双板')
        skill_level = data.get('skill_level', '中级')
        goals = data.get('goals', '提高技术水平')
        
        # 生成学习计划
        plan = chat_manager.generate_learning_plan(ski_type, skill_level, goals, user_id)
        
        return jsonify({'plan': plan})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
