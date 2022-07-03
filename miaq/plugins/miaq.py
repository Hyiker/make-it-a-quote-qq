# -*- coding: utf-8 -*-
from io import BytesIO
from os import path
from nonebot import on_command, on_keyword
from nonebot.rule import to_me, keyword
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, Event
from nonebot.log import logger
import random

from miaq.plugins.reply import extract_reply
from .generate_image import generate


reply_rule = keyword('整个活', '整活', 'makeitaquote')

makeitaquote_cmd = on_command("makeitaquote", rule=to_me(), aliases={"整个活", "整活"}, priority=5)
makeitaquote_msg = on_keyword(["黄鸭"], rule=reply_rule, priority=10)
yiyanwannian = on_command("yiyanwannian", rule=to_me(), aliases={"一眼万年"}, priority=15)

yywn_bio = BytesIO(open("./henhuo/yiyanwannian.jpg", "rb").read())
henhuo = []
with open('henhuo/henhuo.txt', 'r', encoding='utf-8') as f:
    henhuo = f.readlines()

if henhuo == []:
    logger.error("No henhuo found")
    henhuo[0] = "啥也不是！"


async def handler(makeitaquote, event: Event):
    try:
        if event.dict()['message_type'] != 'group':
            return
        logger.info(event.dict())
        reply = await extract_reply(event.dict())
        logger.info("{}, {}, {}".format(reply.user_id, reply.user_card, reply.message))
        imageio = generate(reply)
        await makeitaquote.send("草！走！忽略！ጿ ኈ ቼ ዽ ጿ")
        await makeitaquote.finish(MessageSegment.image(imageio))
    except (KeyError, TypeError) as e:
        logger.error(e)
        await makeitaquote.finish(random.choice(henhuo))


@makeitaquote_cmd.handle()
async def handle_first_receive(bot: Bot, event: Event):
    await handler(makeitaquote_cmd, event)


@makeitaquote_msg.handle()
async def handle_first_receive(bot: Bot, event: Event):
    await handler(makeitaquote_msg, event)


@yiyanwannian.handle()
async def yywn_receive(bot: Bot, event: Event):
    await yiyanwannian.finish(MessageSegment.image(yywn_bio))
