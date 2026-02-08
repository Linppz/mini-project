# src/llm/openai_client.py
from typing import List, AsyncIterator
from openai import AsyncOpenAI
from src.core.config import settings
from src.core.resilience import api_retry  # <--- 改这里：导入你写的重试装饰器
from src.llm.base import BaseLLM
from src.llm.schemas import Message, GenerationConfig, LLMResponse, TokenUsage, Role

class OpenAIClient(BaseLLM):
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")
        
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY.get_secret_value(),
            timeout=settings.LLM_TIMEOUT
        )

    def _format_messages(self, messages: List[Message]) -> List[dict]:
        formatted = []
        for msg in messages:
            role = msg.role.value
            if role == "assistance": # 兼容处理
                role = "assistant"
            formatted.append({"role": role, "content": msg.content})
        return formatted

    @api_retry  # <--- 改这里：使用你的装饰器
    async def generate(self, messages: List[Message], config: GenerationConfig) -> LLMResponse:
        model = settings.LLM_DEFAULT_MODEL if settings.LLM_PROVIDER == "openai" else "gpt-4o-mini"
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=self._format_messages(messages),
            temperature=config.temperature,
            max_tokens=config.max_token,
            top_p=config.top_p,
            stream=False
        )

        choice = response.choices[0]
        usage = response.usage

        return LLMResponse(
            content=choice.message.content or "",
            raw_response=response.model_dump(),
            usage=TokenUsage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens
            ),
            model_name=response.model,
            finish_reason=choice.finish_reason
        )

    # @api_retry  # <--- 改这里
    async def stream(self, messages: List[Message], config: GenerationConfig) -> AsyncIterator[str]:
        model = settings.LLM_DEFAULT_MODEL if settings.LLM_PROVIDER == "openai" else "gpt-4o-mini"
        
        stream = await self.client.chat.completions.create(
            model=model,
            messages=self._format_messages(messages),
            temperature=config.temperature,
            max_tokens=config.max_token,
            top_p=config.top_p,
            stream=True
        )

        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content