# src/core/resilience.py
import logging
from aiolimiter import AsyncLimiter
from src.core.config import settings
import asyncio
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    before_sleep_log
)

# 配置 logger，让我们能看到重试的过程
logger = logging.getLogger("llm_client")

def is_retryable_error(exception: Exception) -> bool:
    """
    判断错误是否值得重试。
    工业界铁律：不要重试 4xx 错误 (除了 429 Rate Limit)。
    只重试网络错误、超时、429 和 5xx 服务端错误。
    """
    
    # 1. 获取错误对象里的 status_code (如果有的话)
    # 大多数库 (httpx, openai, anthropic) 的异常都会带 status_code 属性
    status_code = getattr(exception, "status_code", None)

    if status_code is not None:
        # 429 = Too Many Requests (限流)，必须重试
        if status_code == 429:
            return True
        # 5xx = Server Error (厂商服务器挂了)，必须重试
        if status_code >= 500:
            return True
        # 其他 4xx (400, 401, 403) = 客户端错误，重试无用，直接抛出
        return False

    # 2. 如果没有 status_code，通常是底层的网络错误 (ConnectionError, Timeout)
    # 这些通常是暂时的，值得重试
    # 这里我们简单粗暴地假设没有 status_code 的 Exception 可能是网络波动
    # (在更严格的代码中，我们会检查 isinstance(exception, (ConnectionError, TimeoutError)))
    return True

# 定义一个通用的装饰器，可以直接用在函数上
# 策略：
# 1. wait: 指数退避，从 1秒 开始，最大等待 10秒 (1s -> 2s -> 4s -> 8s ...)
# 2. stop: 最多尝试 3 次 (1次正常调用 + 2次重试)
# 3. retry: 只有 is_retryable_error 返回 True 时才重试
# 4. before_sleep: 每次重试前打印一条日志
api_retry = retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception(is_retryable_error),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)


limiter = AsyncLimiter(max_rate = settings.LLM_RPM, time_period = 60)
concurrency_limiter = asyncio.Semaphore(settings.LLM_MAX_CONCURRENT)