from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, Event
from nonebot.params import CommandArg
from nonebot.log import logger
from .generate_image import generate

makeitaquote = on_command("makeitaquote", rule=to_me(), aliases={"整个活", "整活"}, priority=5)


async def extract_reply(message: dict) -> tuple[int, str, str]:
    """
    提取回复内容
    """
    reply = message['reply']
    sender = reply['sender']
    if sender['card']:
        card = sender['card']
    else:
        card = sender['nickname']
    ret = reply['message'][0]
    return reply['sender']['user_id'], card, ret.data['text']


@makeitaquote.handle()
async def handle_first_receive(bot: Bot, event: Event):
    try:
        if event.dict()['message_type'] != 'group':
            return
        user_id, card, message = await extract_reply(event.dict())
        logger.info("{}, {}, {}".format(user_id, card, message))
        imageio = generate(user_id, card, message)
        await makeitaquote.send("草！走！忽略！ጿ ኈ ቼ ዽ ጿ")
        await makeitaquote.finish(MessageSegment.image(imageio))
    except (KeyError, TypeError) as e:
        logger.error(e)
        await makeitaquote.finish("我上次整活打火机没了，号封一个月，钱扣700多，你有活你整啊，你们这些没钱的才在底下当黑粉儿。")
