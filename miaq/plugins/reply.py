
from dataclasses import dataclass

from nonebot.adapters.onebot.v11.message import Message


@dataclass
class Reply:
    user_id: int = -1
    user_card: str = ""
    message: str = ""
    time: int = -1

    def __repr__(self) -> str:
        return f"{self.user_id} {self.user_card} {self.message} {self.time}"


async def extract_reply(message: dict) -> Reply:
    """
    提取回复内容
    """
    reply = message['reply']
    sender = reply['sender']
    reply_time = reply['time']
    if sender['card']:
        card = sender['card']
    else:
        card = sender['nickname']

    ret = Message(reply['message']).extract_plain_text()
    return Reply(reply['sender']['user_id'], card, ret, reply_time)
