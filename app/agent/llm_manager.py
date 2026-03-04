from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# 尝试导入Google模型
ChatGooglePalm = None

try:
    from langchain_community.chat_models import ChatGooglePalm
except ImportError:
    print("Warning: ChatGooglePalm not available, Google models will be disabled")

# 千问模型现在使用ChatOpenAI通过阿里云百炼的OpenAI兼容接口调用

# 加载环境变量
load_dotenv()

class LLMManager:
    def __init__(self):
        self.models = {
            'openai': self._init_openai,
            'qianwen': self._init_qianwen  # 总是添加千问模型，因为现在使用ChatOpenAI
        }
        
        # 仅在Google模型可用时添加
        if ChatGooglePalm:
            self.models['google'] = self._init_google
            
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
    
    def _init_qianwen(self, model_name='qwen3.5-flash-2026-02-23'):
        """
        初始化千问模型（使用阿里云百炼的OpenAI兼容接口）
        """
        api_key = os.getenv('ALIYUN_DASHSCOPE_KEY') or os.getenv('QIANWEN_API_KEY')
        api_base = os.getenv('ALIYUN_DASHSCOPE_BASE')
        
        if not api_key:
            raise ValueError('Aliyun Dashscope API key not found in environment variables')
        
        if not api_base:
            api_base = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
        
        return ChatOpenAI(
            api_key=api_key,
            model=model_name,
            base_url=api_base,
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
            available_models['qianwen'] = ['qwen3.5-27b', 'qwen3.5-flash-2026-02-23', 'qwen-max', 'qwen-vision', 'qwen-flash-character', 'deepseek-v3.2', 'kimi-k2.5', 'glm-4.7', 'qwen3-max-2026-01-23', 'qwen3-vl-plus-2025-12-19', 'qwen-mt-lite', 'qwen3-max-preview']
            
        return available_models

# 创建全局LLM管理器实例
llm_manager = LLMManager()
