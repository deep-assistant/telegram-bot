import asyncio

from services import tokenizeService, GPTModels


async def hello():
    token = await tokenizeService.create_new_token(1495307231)
    print(token)
    await tokenizeService.update_user_token(1495307231, 10000)
    asd = await tokenizeService.get_user_tokens(1495307231)
    print(asd)


asyncio.run(hello())
