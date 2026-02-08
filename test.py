import asyncio
import sys
from src.llm.factory import LLMFactory
from src.llm.schemas import Message, Role, GenerationConfig
from src.core.config import settings

# 颜色代码，让终端好看点
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"

async def main():
    # 1. 获取客户端 (考察 Factory)
    # 哪怕你调用 100 次 get_client，它也只会实例化 1 次
    client = LLMFactory.get_client() 
    
    print(f"{BLUE}=== 战斗级 LLM Client 终端 ({settings.LLM_PROVIDER}) ==={RESET}")
    print(f"Client ID: {id(client)} (用于验证单例)")
    print("输入 'q' 或 'exit' 退出。\n")

    # 聊天历史 (Context)
    history = [
        Message(role=Role.SYSTEM, content="你是一个乐于助人的 AI 助手，请用简练的中文回答。")
    ]

    while True:
        # 2. 获取用户输入
        user_input = input(f"{GREEN}你: {RESET}")
        if user_input.lower() in ["q", "exit"]:
            break
        
        # 加入历史
        history.append(Message(role=Role.USER, content=user_input))

        # 3. 流式调用 (考察 Stream 接口)
        print(f"{BLUE}AI: {RESET}", end="", flush=True)
        
        full_response = ""
        try:
            # 这里的 client.stream 对上层完全屏蔽了 OpenAI/Anthropic 的差异
            stream = client.stream(
            messages=history,
            config=GenerationConfig(temperature=0.7)
        )

            async for chunk in stream:
                print(chunk, end="", flush=True)
                full_response += chunk
            
            print() # 换行

            # 将 AI 回复加入历史，以便多轮对话
            # 注意：这里需要处理 Role 的定义，如果是 schemas.py 里的 ASSISTANCE 也没关系，Client 内部会转
            history.append(Message(role=Role.ASSISTANCE, content=full_response))

        except Exception as e:
            print(f"\n❌ 出错了: {e}")
            # 如果是 429 或 500，你的 resilience layer 应该已经重试过 3 次了

    # 4. 优雅关闭 (考察资源管理)
    await LLMFactory.close_all()
    print("\n连接已关闭。Bye!")

if __name__ == "__main__":
    # Windows 下 asyncio 的常见策略修复（可选）
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())