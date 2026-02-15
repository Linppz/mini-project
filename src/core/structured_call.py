from src.parser.output_parser import OutputParser
from src.prompt_engine.registry import PromptRegistry
from src.llm.base import BaseLLM
from src.llm.schemas import Message, GenerationConfig, LLMResponse, Role
import asyncio


class StructuredCall():

    def __init__(self, llm_client: BaseLLM, prompt_registry: PromptRegistry, output_parser: OutputParser):
        self.llm_client = llm_client
        self.prompt_registry = prompt_registry
        self.output_parser = output_parser

    async def call(self, prompts : dict, user_template : str, output_schema, max_retries : int =3):
        # 1. 把 output_schema 的 JSON Schema 注入到 prompts 里
        prompts['output_schema'] = output_schema.model_json_schema()
        # 2. 用 prompt_registry.render_and_log() 渲染 prompt
        result = self.prompt_registry.render_and_log(prompts, user_template)
        # 3. 调用 llm_client.generate() 获取 LLM 返回
        messages = [Message(role = Role.USER, content = result.rendered_text)]
        config = GenerationConfig()
        # 5. 如果 ValidationError → 格式化错误 → 追加到消息 → 重试
        for i in range(max_retries):
            try:
                response =  await self.llm_client.generate(messages, config)
                raw_output = response.content
                return self.output_parser.parse(raw_output, output_schema)
            except Exception as e:
                error_message = f"parsing error: {str(e)}. The original output is decoded as: {raw_output}"
                messages.append(Message(role = Role.USER, content = error_message))
        
        # 6. 返回解析后的 Pydantic 对象
        return self.output_parser.parse(raw_output, output_schema)