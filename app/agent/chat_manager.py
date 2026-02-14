from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.agent.llm_manager import llm_manager

class ChatManager:
    def __init__(self, agent_memory, llm_provider='openai', llm_model=None):
        self.agent_memory = agent_memory
        # 初始化大语言模型
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.llm = self._init_llm()
        # 构建滑雪教练prompt
        self.prompt = self._build_ski_coach_prompt()
    
    def _init_llm(self):
        """
        初始化LLM模型
        """
        try:
            return llm_manager.get_llm(self.llm_provider, self.llm_model)
        except Exception as e:
            # 如果初始化失败，返回None，使用模拟回复
            print(f"Failed to initialize LLM: {str(e)}")
            return None
    
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
        
        # 检查LLM是否可用
        llm = self._get_llm()
        if not llm:
            # 如果LLM不可用，返回错误消息
            response = "抱歉，我暂时无法处理您的请求。请检查模型配置并稍后再试。"
        else:
            # 构建对话链
            chain = (
                RunnablePassthrough.assign(
                    chat_history=lambda _: memory.chat_memory.messages
                )
                | self.prompt
                | llm
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
            # 如果LLM未初始化，尝试重新初始化
            try:
                self.llm = llm_manager.get_llm(self.llm_provider, self.llm_model)
            except Exception as e:
                print(f"Failed to initialize LLM: {str(e)}")
                # 如果初始化失败，返回None
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
        try:
            # 使用真实的LLM生成回复
            response = chain.invoke({"input": message})
            return response
        except Exception as e:
            print(f"Failed to generate response: {str(e)}")
            # 如果LLM调用失败，返回错误消息
            return "抱歉，我暂时无法处理您的请求。请稍后再试。"
    
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
        # 构建视频分析的prompt
        video_analysis_prompt = f"""请分析以下滑雪视频并提供专业评价：

视频路径：{video_path}
滑雪类型：{ski_type}
滑雪者水平：{skill_level}

请从以下几个方面进行分析：
1. 技术评价：分析滑雪者的姿势、动作、平衡等技术方面的表现
2. 改进建议：指出需要改进的地方并提供具体的改进方法
3. 学习计划：基于当前水平，建议下一步的学习重点
4. 安全提示：提供相关的安全建议
5. 总体评分：给滑雪者的表现打分（0-100）

请提供详细、专业、有针对性的分析和建议。
"""
        
        # 使用LLM生成分析结果
        try:
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
            
            # 生成分析结果
            analysis_text = self._generate_response(chain, video_analysis_prompt)
            
            # 构建分析结果字典
            analysis = {
                'message': '视频分析完成！',
                'evaluation': {
                    'technical_evaluation': analysis_text,
                    'improvement_suggestions': '',
                    'learning_plan': '',
                    'safety_tips': '',
                    'overall_rating': ''
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
        except Exception as e:
            print(f"Failed to analyze video: {str(e)}")
            # 如果分析失败，返回错误消息
            return {
                'message': '视频分析失败',
                'evaluation': {
                    'technical_evaluation': '抱歉，视频分析暂时无法完成。请稍后再试。',
                    'improvement_suggestions': '',
                    'learning_plan': '',
                    'safety_tips': '',
                    'overall_rating': ''
                }
            }
