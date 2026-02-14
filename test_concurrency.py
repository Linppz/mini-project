import asyncio
from src.llm.factory import LLMFactory
from src.llm.schemas import Message, Role, GenerationConfig
from src.core.config import settings
from src.core.resilience import limiter, concurrency_limiter
from datetime import datetime


async def singletask(client, task_id, prompt):
    async with limiter:
        async with concurrency_limiter:
            start_time = datetime.now()
            if task_id == 14:
                raise Exception('模拟失败')
            print(f'{task_id}开始行动')
            result = await client.generate(prompt, GenerationConfig())
            # print(f"林鹏蓁的大魔丸: {result.content} ")
            end_time = datetime.now()
            print(f'{task_id}结束行动，耗时{end_time - start_time}秒')

async def run_batch():
    client = LLMFactory.get_client()
    prompt = []
    prompt.append(Message(role=Role.USER, content = "谁是孔子"))
    box = []
    for i in range(1, 21):
        box.append(singletask(client, i, prompt))

    result = await asyncio.gather(*box, return_exceptions = True)

    for i,s in enumerate(result, 1):
        if isinstance(s, Exception):
            print(f"第{i}个任务失败了")
    await LLMFactory.close_all()
    print(f"接口已关闭")


# async def main():
#     sem = asyncio.Semaphore(6)
#     client = LLMFactory.get_client()
#     prompt: list = []
#     prompt.append(Message(role=Role.USER, content="白雪公主的名字"))
#     box:list = []
#     for i in range(1, 21):
#         box.append(singletask(client, i, prompt,sem))
#     result = await asyncio.gather(*box)

if __name__ == '__main__':

    # asyncio.run(main())
    asyncio.run(run_batch())





