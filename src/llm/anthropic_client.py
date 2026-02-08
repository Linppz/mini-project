# src/llm/anthropic_client.py
from typing import List, AsyncIterator, Tuple
from anthropic import AsyncAnthropic
from src.core.config import settings
from src.core.resilience import api_retry  # <--- 改这里
from src.llm.base import BaseLLM
from src.llm.schemas import Message, GenerationConfig, LLMResponse, TokenUsage, Role

class AnthropicClient(BaseLLM):
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set.")
            
        self.client = AsyncAnthropic(
            api_key=settings.ANTHROPIC_API_KEY.get_secret_value(),
            timeout=settings.LLM_TIMEOUT
        )

    def _prepare_inputs(self, messages: List[Message]) -> Tuple[str, List[dict]]:
        system_prompt = ""
        anthropic_messages = []
        for msg in messages:
            if msg.role == Role.SYSTEM:
                system_prompt = msg.content
            else:
                role = "assistant" if msg.role.value == "assistance" else msg.role.value
                anthropic_messages.append({"role": role, "content": msg.content})
        return system_prompt, anthropic_messages

    @api_retry  # <--- 改这里
    async def generate(self, messages: List[Message], config: GenerationConfig) -> LLMResponse:
        system_prompt, formatted_messages = self._prepare_inputs(messages)
        # 这里的 model 建议也从 settings 读取，这里简化处理
        model = "claude-3-5-sonnet-20240620" 
        
        response = await self.client.messages.create(
            model=model,
            system=system_prompt,
            messages=formatted_messages,
            temperature=config.temperature,
            max_tokens=config.max_token or 1024,
            top_p=config.top_p,
            stream=False
        )

        content_text = ""
        if response.content and response.content[0].type == 'text':
            content_text = response.content[0].text

        return LLMResponse(
            content=content_text,
            raw_response=response.model_dump(),
            usage=TokenUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens
            ),
            model_name=response.model,
            finish_reason=response.stop_reason
        )

    @api_retry  # <--- 改这里
    async def stream(self, messages: List[Message], config: GenerationConfig) -> AsyncIterator[str]:
        system_prompt, formatted_messages = self._prepare_inputs(messages)
        model = "claude-3-5-sonnet-20240620"

        stream = await self.client.messages.create(
            model=model,
            system=system_prompt,
            messages=formatted_messages,
            temperature=config.temperature,
            max_tokens=config.max_token or 1024,
            top_p=config.top_p,
            stream=True
        )

        async for event in stream:
            if event.type == "content_block_delta" and event.delta.type == "text_delta":
                yield event.delta.text