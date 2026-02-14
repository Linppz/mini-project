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
            if task_id == 14 or task_id == 17 or task_id == 20:
                raise Exception('模拟失败')
            print(f'{task_id}开始行动')
            async for word in client.stream(prompt, GenerationConfig()):
                print(word, end = "", flush=True)
            print(f'本次消费token:{client.tracker.get_usage()}')
            end_time = datetime.now()
            print(f'{task_id}结束行动，耗时{end_time - start_time}秒')

async def run_batch():
    client = LLMFactory.get_client()
    prompt = []
    prompt.append(Message(role=Role.USER, content = "谁是孔子"))
    # box = []
    # for i in range(1, 51):
        # box.append(singletask(client, i, prompt))
    # start_time = datetime.now()
    # result = await asyncio.gather(*box, return_exceptions = True)
    # end_time = datetime.now()
    result = await singletask(client, 1,prompt)
    # success_time = len(box)
    # for i,s in enumerate(result, 1):
    #     if isinstance(s, Exception):
    #         success_time-=1
    #         print(f"第{i}个任务失败了")
    # print(f'总耗时{end_time - start_time} 秒, 平均耗时为{(end_time - start_time) / 50} 秒')
    # print(f'总成功了{ success_time} 个, 失败了{len(box) - success_time}')
    await LLMFactory.close_all()
    # print(f"接口已关闭")



if __name__ == '__main__':

    # asyncio.run(main())
    asyncio.run(run_batch())





