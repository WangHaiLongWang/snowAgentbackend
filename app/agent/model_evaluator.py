import base64
import os
import requests
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

class ModelEvaluator:
    def __init__(self):
        # 初始化大语言模型
        # 注意：实际项目中需要从环境变量或配置文件中读取API密钥
        self.llm = None
    
    def evaluate(self, frames, pose_data, ski_type, skill_level):
        """
        评价滑雪动作
        
        Args:
            frames: 帧路径列表
            pose_data: 姿态数据列表
            ski_type: 滑雪类型（单板/双板）
            skill_level: 技能水平（初级/中级/高级）
            
        Returns:
            evaluation: 评价结果
        """
        # 构建评价prompt
        prompt = self._build_evaluation_prompt(ski_type, skill_level, pose_data)
        
        # 生成评价结果
        # 注意：实际项目中应该调用真实的多模态大语言模型API
        evaluation = self._generate_evaluation(prompt, frames)
        
        return evaluation
    
    def _build_evaluation_prompt(self, ski_type, skill_level, pose_data):
        """
        构建评价prompt
        
        Args:
            ski_type: 滑雪类型
            skill_level: 技能水平
            pose_data: 姿态数据
            
        Returns:
            prompt: 评价prompt
        """
        prompt = f"你是一位专业的滑雪教练，精通{ski_type}滑雪技术，从初级到顶级水平都有丰富的教学经验。现在请你分析一位{skill_level}滑雪者的动作，并提供专业的评价和改进建议。\n\n"
        
        # 添加姿态数据分析
        if pose_data:
            prompt += "## 姿态数据分析\n"
            
            # 计算平均角度
            avg_angles = self._calculate_average_angles(pose_data)
            
            if avg_angles:
                prompt += f"- 左膝角度: {avg_angles.get('left_knee', 'N/A'):.1f}°\n"
                prompt += f"- 右膝角度: {avg_angles.get('right_knee', 'N/A'):.1f}°\n"
                prompt += f"- 左髋角度: {avg_angles.get('left_hip', 'N/A'):.1f}°\n"
                prompt += f"- 右髋角度: {avg_angles.get('right_hip', 'N/A'):.1f}°\n"
                prompt += f"- 左肩角度: {avg_angles.get('left_shoulder', 'N/A'):.1f}°\n"
                prompt += f"- 右肩角度: {avg_angles.get('right_shoulder', 'N/A'):.1f}°\n\n"
        
        prompt += "## 评价要求\n"
        prompt += "1. 技术评价：分析滑雪者的动作是否标准，指出优点和不足之处\n"
        prompt += "2. 改进建议：针对不足之处，提供具体的改进方法和练习建议\n"
        prompt += "3. 学习计划：根据滑雪者的当前水平，推荐下一步学习的技巧和练习\n"
        prompt += "4. 安全提示：提供相关的安全注意事项\n\n"
        prompt += "请基于提供的视频帧和姿态数据，给出详细、专业的评价。"
        
        return prompt
    
    def _calculate_average_angles(self, pose_data):
        """
        计算平均角度
        
        Args:
            pose_data: 姿态数据列表
            
        Returns:
            avg_angles: 平均角度字典
        """
        if not pose_data:
            return {}
        
        angles_sum = {}
        angles_count = {}
        
        for data in pose_data:
            if 'angles' in data:
                for angle_name, angle_value in data['angles'].items():
                    if angle_value is not None:
                        if angle_name not in angles_sum:
                            angles_sum[angle_name] = 0
                            angles_count[angle_name] = 0
                        angles_sum[angle_name] += angle_value
                        angles_count[angle_name] += 1
        
        avg_angles = {}
        for angle_name, total in angles_sum.items():
            count = angles_count.get(angle_name, 1)
            avg_angles[angle_name] = total / count
        
        return avg_angles
    
    def _generate_evaluation(self, prompt, frames):
        """
        生成评价结果
        
        Args:
            prompt: 评价prompt
            frames: 帧路径列表
            
        Returns:
            evaluation: 评价结果
        """
        # 注意：实际项目中应该调用真实的多模态大语言模型API
        # 这里使用模拟的评价结果
        
        # 模拟评价结果
        evaluation = {
            'technical_evaluation': '滑雪者的基本姿势保持良好，膝盖微屈，身体重心适中。转弯时的身体跟随动作基本协调，但在高速转弯时上半身过于僵硬，缺乏柔韧性。',
            'improvement_suggestions': '1. 加强核心力量训练，提高身体稳定性\n2. 练习转弯时的身体跟随动作，保持上半身放松\n3. 注意手臂的位置，保持自然摆动\n4. 增加平衡训练，提高在不平 terrain 上的稳定性',
            'learning_plan': '基于当前水平，建议下一步学习：\n1. 中级转弯技巧：练习更流畅的Carving转弯\n2. 速度控制：学习使用身体姿势控制速度\n3. 地形适应：练习在不同坡度和雪质上的滑行\n4. 安全技巧：学习紧急制动和规避障碍物',
            'safety_tips': '1. 始终保持对前方的观察，提前规划路线\n2. 控制速度，特别是在不熟悉的雪道上\n3. 佩戴必要的护具，如头盔、护膝等\n4. 遵守雪道规则，尊重其他滑雪者',
            'overall_rating': '良好（75/100）'
        }
        
        # 实际项目中，这里应该调用真实的API
        # 例如使用OpenAI的GPT-4V
        # if frames:
        #     # 编码第一帧作为示例
        #     with open(frames[0], "rb") as f:
        #         base64_image = base64.b64encode(f.read()).decode('utf-8')
        #     
        #     messages = [
        #         HumanMessage(
        #             content=[
        #                 {"type": "text", "text": prompt},
        #                 {
        #                     "type": "image_url",
        #                     "image_url": {
        #                         "url": f"data:image/jpeg;base64,{base64_image}"
        #                     },
        #                 },
        #             ]
        #         )
        #     ]
        #     
        #     if self.llm:
        #         response = self.llm.invoke(messages)
        #         # 解析响应
        #         evaluation = self._parse_llm_response(response.content)
        
        return evaluation
    
    def _parse_llm_response(self, response):
        """
        解析大语言模型的响应
        
        Args:
            response: 模型响应
            
        Returns:
            evaluation: 结构化的评价结果
        """
        # 注意：实际项目中需要根据模型的响应格式进行解析
        # 这里使用简化的实现
        
        evaluation = {
            'technical_evaluation': '技术评价',
            'improvement_suggestions': '改进建议',
            'learning_plan': '学习计划',
            'safety_tips': '安全提示',
            'overall_rating': '总体评分'
        }
        
        # 简单的解析逻辑
        if '技术评价' in response:
            tech_start = response.find('技术评价')
            improvement_start = response.find('改进建议')
            if tech_start != -1 and improvement_start != -1:
                evaluation['technical_evaluation'] = response[tech_start:improvement_start].strip()
        
        if '改进建议' in response:
            improvement_start = response.find('改进建议')
            plan_start = response.find('学习计划')
            if improvement_start != -1 and plan_start != -1:
                evaluation['improvement_suggestions'] = response[improvement_start:plan_start].strip()
        
        if '学习计划' in response:
            plan_start = response.find('学习计划')
            safety_start = response.find('安全提示')
            if plan_start != -1 and safety_start != -1:
                evaluation['learning_plan'] = response[plan_start:safety_start].strip()
        
        if '安全提示' in response:
            safety_start = response.find('安全提示')
            if safety_start != -1:
                evaluation['safety_tips'] = response[safety_start:].strip()
        
        return evaluation
