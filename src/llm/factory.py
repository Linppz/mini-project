# src/llm/factory.py
from typing import Dict, Optional
import logging

from src.core.config import settings
from src.llm.base import BaseLLM
from src.llm.openai_client import OpenAIClient
from src.llm.deepseek_client import DeepSeekClient
from src.llm.anthropic_client import AnthropicClient

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    LLM 客户端工厂与生命周期管理器。
    实现单例模式：确保每个 Provider 在全局只有一个实例，从而复用 TCP 连接池。
    """

    # 单例注册表：存储已实例化的客户端
    # Key: provider_name (e.g., "openai", "deepseek"), Value: Client Instance
    _instances: Dict[str, BaseLLM] = {}

    @classmethod
    def get_client(cls, provider: Optional[str] = None) -> BaseLLM:
        """
        获取 LLM 客户端实例。如果不存在则创建，如果存在则直接返回。

        Args:
            provider: 指定厂商 (openai, deepseek, anthropic)。
                      如果不传，则使用 settings.LLM_PROVIDER 配置的默认值。
        """
        if provider is None:
            provider = settings.LLM_PROVIDER

        # 1. 检查缓存中是否已有该实例
        if provider in cls._instances:
            return cls._instances[provider]

        # 2. 如果没有，则创建新实例 (Lazy Initialization)
        logger.info(f"Initializing new LLM client for provider: {provider}")

        client: BaseLLM

        if provider == "openai":
            client = OpenAIClient()
        elif provider == "deepseek":
            client = DeepSeekClient()
        elif provider == "anthropic":
            client = AnthropicClient()
        else:
            raise ValueError(f"Unsupported LLM Provider: {provider}")

        # 3. 存入缓存并返回
        cls._instances[provider] = client
        return client

    @classmethod
    async def close_all(cls):
        """
        关闭所有客户端连接。
        必须在程序退出前调用，防止 ResourceWarning 和连接泄漏。
        """
        logger.info("Closing all LLM client connections...")
        for provider, client in cls._instances.items():
            # 获取内部的 SDK client (AsyncOpenAI, AsyncAnthropic 等)
            # 假设所有 Client 实现都把 SDK 实例存在 self.client 属性上
            if hasattr(client, "client"):
                # 大多数异步 SDK (OpenAI, Anthropic) 都有 close 方法
                # 注意：有些库是 close(), 有些是 aclose()，这里做个防御性编程
                raw_client = getattr(client, "client")

                if hasattr(raw_client, "close"):
                    # 同步或异步方法检测
                    import inspect
                    if inspect.iscoroutinefunction(raw_client.close):
                        await raw_client.close()
                    else:
                        # 尝试找 aclose (httpx 风格)
                        if hasattr(raw_client, "aclose"):
                            await raw_client.aclose()
                        else:
                            # 确实是同步 close，但在 async 环境下调用也没问题
                            raw_client.close()

            logger.debug(f"Closed {provider} client.")

        cls._instances.clear()
        logger.info("All LLM clients closed.")


# 为了方便导入，直接暴露一个获取默认 client 的快捷函数
def get_default_llm() -> BaseLLM:
    return LLMFactory.get_client()