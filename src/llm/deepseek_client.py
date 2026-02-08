# src/llm/deepseek_client.py
from typing import List
from openai import AsyncOpenAI
from src.core.config import settings
from src.llm.schemas import Message, GenerationConfig, LLMResponse
from src.llm.openai_client import OpenAIClient
from src.core.resilience import api_retry # 如果你需要重写 generate，记得引入这个

class DeepSeekClient(OpenAIClient):
    def __init__(self):
        if not settings.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY is not set.")
            
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY.get_secret_value(),
            base_url="https://api.deepseek.com",
            timeout=settings.LLM_TIMEOUT
        )
    
    # generate 和 stream 直接继承父类，无需修改代码
    # 如果你要重写 generate，记得加上 @api_retry
    
    @api_retry 
    async def generate(self, messages: List[Message], config: GenerationConfig) -> LLMResponse:
        # 即使继承，为了保险起见或处理特殊模型名，重写并加上装饰器也是好的实践
        original_model = settings.LLM_DEFAULT_MODEL
        target_model = "deepseek-chat" if "gpt" in original_model else original_model
        
        response = await self.client.chat.completions.create(
            model=target_model,
            messages=self._format_messages(messages),
            temperature=config.temperature,
            max_tokens=config.max_token,
            top_p=config.top_p,
            stream=False
        )
        
        # 复用父类的数据清洗逻辑略显麻烦，这里简单拷贝返回逻辑
        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            content=choice.message.content or "",
            raw_response=response.model_dump(),
            usage={ # 简单构造 Dict 传给 Pydantic
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            },
            model_name=response.model,
            finish_reason=choice.finish_reason
        )