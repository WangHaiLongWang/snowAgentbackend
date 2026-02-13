from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
import json
import os
from datetime import datetime

class AgentMemory:
    def __init__(self):
        # 初始化对话记忆存储
        self.memories = {}
        # 初始化用户滑雪历史存储
        self.ski_history = {}
        # 初始化用户学习计划存储
        self.learning_plans = {}
    
    def get_memory(self, user_id):
        """
        获取用户的对话记忆
        
        Args:
            user_id: 用户ID
            
        Returns:
            memory: 对话记忆对象
        """
        if user_id not in self.memories:
            # 创建新的对话记忆
            self.memories[user_id] = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
                input_key="input"
            )
        
        return self.memories[user_id]
    
    def add_message(self, user_id, role, content):
        """
        添加消息到对话记忆
        
        Args:
            user_id: 用户ID
            role: 角色（user/assistant）
            content: 消息内容
        """
        memory = self.get_memory(user_id)
        
        # 根据角色添加消息
        if role == "user":
            memory.save_context({"input": content}, {"output": ""})
        elif role == "assistant":
            # 获取最后一条消息
            if memory.chat_memory.messages:
                last_message = memory.chat_memory.messages[-1]
                # 更新助手的回复
                memory.chat_memory.messages[-1].content = content
            else:
                # 如果没有消息，创建一个新的
                memory.save_context({"input": ""}, {"output": content})
    
    def get_history(self, user_id):
        """
        获取对话历史
        
        Args:
            user_id: 用户ID
            
        Returns:
            history: 对话历史列表
        """
        if user_id not in self.memories:
            return []
        
        memory = self.memories[user_id]
        history = []
        
        # 转换为前端可用的格式
        for i, message in enumerate(memory.chat_memory.messages):
            if i % 2 == 0:
                # 用户消息
                history.append({
                    "role": "user",
                    "content": message.content
                })
            else:
                # 助手消息
                history.append({
                    "role": "assistant",
                    "content": message.content
                })
        
        return history
    
    def clear_history(self, user_id):
        """
        清空对话历史
        
        Args:
            user_id: 用户ID
        """
        if user_id in self.memories:
            del self.memories[user_id]
    
    def add_ski_history(self, user_id, ski_data):
        """
        添加滑雪历史
        
        Args:
            user_id: 用户ID
            ski_data: 滑雪数据
        """
        if user_id not in self.ski_history:
            self.ski_history[user_id] = []
        
        # 添加时间戳
        ski_data['timestamp'] = datetime.now().isoformat()
        self.ski_history[user_id].append(ski_data)
    
    def get_ski_history(self, user_id):
        """
        获取滑雪历史
        
        Args:
            user_id: 用户ID
            
        Returns:
            history: 滑雪历史列表
        """
        if user_id not in self.ski_history:
            return []
        
        return self.ski_history[user_id]
    
    def save_learning_plan(self, user_id, plan):
        """
        保存学习计划
        
        Args:
            user_id: 用户ID
            plan: 学习计划
        """
        if user_id not in self.learning_plans:
            self.learning_plans[user_id] = []
        
        # 添加时间戳
        plan_data = {
            'plan': plan,
            'created_at': datetime.now().isoformat()
        }
        self.learning_plans[user_id].append(plan_data)
    
    def get_learning_plan(self, user_id):
        """
        获取学习计划
        
        Args:
            user_id: 用户ID
            
        Returns:
            plan: 最新的学习计划
        """
        if user_id not in self.learning_plans or not self.learning_plans[user_id]:
            return None
        
        # 返回最新的学习计划
        return self.learning_plans[user_id][-1]
    
    def get_user_profile(self, user_id):
        """
        获取用户 profile，包含对话历史、滑雪历史和学习计划
        
        Args:
            user_id: 用户ID
            
        Returns:
            profile: 用户 profile
        """
        profile = {
            'chat_history': self.get_history(user_id),
            'ski_history': self.get_ski_history(user_id),
            'learning_plan': self.get_learning_plan(user_id)
        }
        
        return profile
    
    def save_to_disk(self, user_id, file_path=None):
        """
        保存用户数据到磁盘
        
        Args:
            user_id: 用户ID
            file_path: 文件路径
        """
        if not file_path:
            # 默认保存路径
            file_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'data',
                f'user_{user_id}.json'
            )
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 准备数据
        data = {
            'chat_history': self.get_history(user_id),
            'ski_history': self.get_ski_history(user_id),
            'learning_plans': self.learning_plans.get(user_id, [])
        }
        
        # 保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_disk(self, user_id, file_path=None):
        """
        从磁盘加载用户数据
        
        Args:
            user_id: 用户ID
            file_path: 文件路径
        """
        if not file_path:
            # 默认加载路径
            file_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'data',
                f'user_{user_id}.json'
            )
        
        if not os.path.exists(file_path):
            return
        
        # 加载数据
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 恢复对话历史
        if 'chat_history' in data:
            memory = self.get_memory(user_id)
            # 清空现有历史
            memory.clear()
            # 添加历史消息
            for msg in data['chat_history']:
                self.add_message(user_id, msg['role'], msg['content'])
        
        # 恢复滑雪历史
        if 'ski_history' in data:
            self.ski_history[user_id] = data['ski_history']
        
        # 恢复学习计划
        if 'learning_plans' in data:
            self.learning_plans[user_id] = data['learning_plans']
