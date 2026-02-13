from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

class ChatManager:
    def __init__(self, agent_memory):
        self.agent_memory = agent_memory
        # 初始化大语言模型
        # 注意：实际项目中需要从环境变量或配置文件中读取API密钥
        self.llm = None
        # 构建滑雪教练prompt
        self.prompt = self._build_ski_coach_prompt()
    
    def _build_ski_coach_prompt(self):
        """
        构建滑雪教练prompt
        
        Returns:
            prompt: 滑雪教练prompt
        """
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "你是一位专业的滑雪教练，精通单双板滑雪技术，从初级到顶级水平都有丰富的教学经验。\n"
                "你的专业领域包括：\n"
                "- 搓雪小回转\n"
                "- 刻滑\n"
                "- 刻平\n"
                "- 平花\n"
                "- 公园技巧\n"
                "- 其他各种滑雪技巧和底层逻辑\n"
                "你能够：\n"
                "1. 根据用户上传的视频进行分析，指出动作中的问题并提供改进建议\n"
                "2. 根据用户的技术水平和学习目标，制定个性化的学习计划\n"
                "3. 回答用户关于滑雪技术、装备、雪场等方面的问题\n"
                "4. 与用户进行专业、友好的对话，提供有价值的滑雪知识和建议\n"
                "你的回答应该：\n"
                "- 专业、准确，基于滑雪技术的科学原理\n"
                "- 清晰、易懂，避免使用过于专业的术语\n"
                "- 个性化，考虑用户的技术水平和学习目标\n"
                "- 鼓励性，激发用户的学习热情\n"
                "- 安全第一，强调滑雪安全的重要性\n"
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        return prompt
    
    def handle_message(self, message, user_id):
        """
        处理用户消息
        
        Args:
            message: 用户消息
            user_id: 用户ID
            
        Returns:
            response: 助手回复
        """
        # 获取用户的对话记忆
        memory = self.agent_memory.get_memory(user_id)
        
        # 构建对话链
        chain = (
            RunnablePassthrough.assign(
                chat_history=lambda _: memory.chat_memory.messages
            )
            | self.prompt
            | self._get_llm()
            | StrOutputParser()
        )
        
        # 生成回复
        response = self._generate_response(chain, message)
        
        # 保存对话到记忆
        self.agent_memory.add_message(user_id, "user", message)
        self.agent_memory.add_message(user_id, "assistant", response)
        
        return response
    
    def generate_learning_plan(self, ski_type, skill_level, goals, user_id):
        """
        生成学习计划
        
        Args:
            ski_type: 滑雪类型（单板/双板）
            skill_level: 当前技能水平
            goals: 学习目标
            user_id: 用户ID
            
        Returns:
            plan: 学习计划
        """
        # 构建学习计划prompt
        plan_prompt = f"请为一位{skill_level}水平的{ski_type}滑雪者制定一个学习计划，目标是{goals}。\n\n"
        plan_prompt += "学习计划应该包括：\n"
        plan_prompt += "1. 短期目标（1-2周）\n"
        plan_prompt += "2. 中期目标（1-2个月）\n"
        plan_prompt += "3. 长期目标（3-6个月）\n"
        plan_prompt += "4. 每周练习计划，包括具体的练习内容和时间安排\n"
        plan_prompt += "5. 技术要点和注意事项\n"
        plan_prompt += "6. 安全提示\n"
        plan_prompt += "7. 装备建议（如适用）\n\n"
        plan_prompt += "请根据滑雪者的水平和目标，制定详细、实用的学习计划。"
        
        # 生成学习计划
        response = self.handle_message(plan_prompt, user_id)
        
        # 保存学习计划
        self.agent_memory.save_learning_plan(user_id, response)
        
        return response
    
    def _get_llm(self):
        """
        获取大语言模型
        
        Returns:
            llm: 大语言模型对象
        """
        if not self.llm:
            # 注意：实际项目中需要从环境变量或配置文件中读取API密钥
            # 这里使用模拟的LLM
            self.llm = None
        
        return self.llm
    
    def _generate_response(self, chain, message):
        """
        生成回复
        
        Args:
            chain: 对话链
            message: 用户消息
            
        Returns:
            response: 助手回复
        """
        # 注意：实际项目中应该使用真实的LLM
        # 这里使用模拟的回复
        
        # 基于用户消息生成模拟回复
        if any(keyword in message.lower() for keyword in ['你好', 'hi', 'hello', '开始']):
            return "你好！我是你的专业滑雪教练。很高兴为你提供帮助。请问你是单板还是双板滑雪者？当前的技术水平如何？有什么具体的滑雪问题或学习目标吗？"
        
        elif any(keyword in message.lower() for keyword in ['单板', '双板']):
            return "了解了！单板和双板各有特色，都非常有趣。请问你目前的技术水平如何？是初级、中级还是高级？你最近在练习什么技巧，或者有什么具体的问题需要帮助？"
        
        elif any(keyword in message.lower() for keyword in ['技术', '技巧', '动作']):
            return "关于滑雪技术，我可以给你提供详细的指导。请问你具体想了解哪方面的技巧？比如转弯、刹车、跳跃等。另外，你当前的技术水平是什么样的？这样我可以给你更有针对性的建议。"
        
        elif any(keyword in message.lower() for keyword in ['学习计划', '练习', '进步']):
            return "制定学习计划是提高滑雪技术的重要环节。为了给你制定合适的计划，我需要了解：1. 你是单板还是双板？2. 当前的技术水平？3. 你的学习目标是什么？4. 每周大概能有多少时间练习？"
        
        elif any(keyword in message.lower() for keyword in ['装备', '雪板', '雪鞋']):
            return "装备对于滑雪体验和技术发挥非常重要。请问你是想了解初学者的装备选择，还是需要根据你的技术水平推荐更专业的装备？另外，你是单板还是双板滑雪者？"
        
        elif any(keyword in message.lower() for keyword in ['安全', '危险', '受伤']):
            return "滑雪安全是第一位的！以下是一些重要的安全提示：1. 始终佩戴头盔和必要的护具；2. 选择适合自己水平的雪道；3. 控制速度，特别是在人多或不熟悉的区域；4. 遵守雪道规则，尊重其他滑雪者；5. 了解基本的急救知识。请问你有具体的安全问题吗？"
        
        else:
            return "感谢你的问题！作为专业的滑雪教练，我可以为你提供关于滑雪技术、装备、学习计划、安全等方面的建议。请问你具体想了解什么？或者你可以上传你的滑雪视频，我会为你分析动作并提供改进建议。"
    
    def analyze_video(self, video_path, ski_type, skill_level, user_id):
        """
        分析视频并提供评价
        
        Args:
            video_path: 视频路径
            ski_type: 滑雪类型
            skill_level: 技能水平
            user_id: 用户ID
            
        Returns:
            analysis: 分析结果
        """
        # 这里应该调用视频处理和分析模块
        # 为了简化，这里返回模拟的分析结果
        
        analysis = {
            'message': '视频分析完成！',
            'evaluation': {
                'technical_evaluation': '你的基本姿势保持良好，膝盖微屈，身体重心适中。转弯时的身体跟随动作基本协调，但在高速转弯时上半身过于僵硬，缺乏柔韧性。',
                'improvement_suggestions': '1. 加强核心力量训练，提高身体稳定性\n2. 练习转弯时的身体跟随动作，保持上半身放松\n3. 注意手臂的位置，保持自然摆动\n4. 增加平衡训练，提高在不平 terrain 上的稳定性',
                'learning_plan': '基于当前水平，建议下一步学习：\n1. 中级转弯技巧：练习更流畅的Carving转弯\n2. 速度控制：学习使用身体姿势控制速度\n3. 地形适应：练习在不同坡度和雪质上的滑行\n4. 安全技巧：学习紧急制动和规避障碍物',
                'safety_tips': '1. 始终保持对前方的观察，提前规划路线\n2. 控制速度，特别是在不熟悉的雪道上\n3. 佩戴必要的护具，如头盔、护膝等\n4. 遵守雪道规则，尊重其他滑雪者',
                'overall_rating': '良好（75/100）'
            }
        }
        
        # 保存分析结果到用户历史
        ski_data = {
            'video_path': video_path,
            'ski_type': ski_type,
            'skill_level': skill_level,
            'analysis': analysis
        }
        self.agent_memory.add_ski_history(user_id, ski_data)
        
        return analysis
