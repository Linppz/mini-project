# src/llm/base.py
from abc import ABC, abstractmethod
from typing import List, AsyncIterator
from src.llm.schemas import LLMResponse, Message, GenerationConfig

class BaseLLM(ABC):
    """
    LLM 客户端的抽象基类 (Abstract Base Class)。
    它是所有具体模型实现（OpenAI, DeepSeek等）必须遵守的契约。
    """

    @abstractmethod
    async def generate(self, messages: List[Message], config: GenerationConfig) -> LLMResponse:
        """
        [非流式] 生成完整的回复。
        
        Args:
            messages: 聊天历史列表 [Message(role='user', content='...'), ...]
            config: 生成参数配置 (temperature, max_tokens 等)
            
        Returns:
            LLMResponse: 统一封装的响应对象
        """
        pass

    @abstractmethod
    async def stream(self, messages: List[Message], config: GenerationConfig) -> AsyncIterator[str]:
        """
        [流式] 逐步生成回复（打字机效果）。
        
        Args:
            messages: 聊天历史列表
            config: 生成参数配置
            
        Returns:
            AsyncIterator[str]: 异步生成的内容片段流
        """
        pass