from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# 尝试导入Google和千问模型
ChatGooglePalm = None
QianwenChat = None

try:
    from langchain_community.chat_models import ChatGooglePalm
except ImportError:
    print("Warning: ChatGooglePalm not available, Google models will be disabled")

try:
    from langchain_community.chat_models import QianwenChat
except ImportError:
    print("Warning: QianwenChat not available, Qianwen models will be disabled")

# 加载环境变量
load_dotenv()

class LLMManager:
    def __init__(self):
        self.models = {
            'openai': self._init_openai
        }
        
        # 仅在模型可用时添加
        if ChatGooglePalm:
            self.models['google'] = self._init_google
        
        if QianwenChat:
            self.models['qianwen'] = self._init_qianwen
            
        self.llm_instances = {}
    
    def _init_openai(self, model_name='gpt-3.5-turbo'):
        """
        初始化OpenAI模型
        """
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError('OpenAI API key not found in environment variables')
        
        return ChatOpenAI(
            api_key=api_key,
            model_name=model_name,
            temperature=0.7
        )
    
    def _init_google(self, model_name='gemini-pro'):
        """
        初始化Google模型
        """
        if not ChatGooglePalm:
            raise ValueError('Google model not available')
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError('Google API key not found in environment variables')
        
        return ChatGooglePalm(
            google_api_key=api_key,
            model_name=model_name,
            temperature=0.7
        )
    
    def _init_qianwen(self, model_name='ep-20240101181146-95mzh'):
        """
        初始化千问模型
        """
        if not QianwenChat:
            raise ValueError('Qianwen model not available')
        
        api_key = os.getenv('QIANWEN_API_KEY')
        if not api_key:
            raise ValueError('Qianwen API key not found in environment variables')
        
        return QianwenChat(
            qianwen_api_key=api_key,
            model_name=model_name,
            temperature=0.7
        )
    
    def get_llm(self, provider='openai', model_name=None):
        """
        获取LLM实例
        
        Args:
            provider: 模型提供商 (openai/google/qianwen)
            model_name: 模型名称
            
        Returns:
            llm: LLM实例
        """
        # 生成缓存键
        cache_key = f"{provider}_{model_name or 'default'}"
        
        # 检查缓存
        if cache_key in self.llm_instances:
            return self.llm_instances[cache_key]
        
        # 初始化模型
        if provider not in self.models:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
        try:
            llm = self.models[provider](model_name)
            self.llm_instances[cache_key] = llm
            return llm
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM: {str(e)}")
    
    def get_available_models(self):
        """
        获取可用的模型列表
        
        Returns:
            models: 可用模型列表
        """
        available_models = {
            'openai': ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo']
        }
        
        if ChatGooglePalm:
            available_models['google'] = ['gemini-pro', 'gemini-ultra']
        
        if QianwenChat:
            available_models['qianwen'] = ['ep-20240101181146-95mzh', 'ep-20240101181146-95mzh-pro']
            
        return available_models

# 创建全局LLM管理器实例
llm_manager = LLMManager()
