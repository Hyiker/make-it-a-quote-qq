# coding:utf-8
import requests
from io import BytesIO
from pilmoji import Pilmoji
from pilmoji.source import MicrosoftEmojiSource
from PIL import Image, ImageDraw, ImageFont
from time import localtime, strftime, time
import math
import textwrap

from miaq.plugins.reply import Reply


AVATAR_URL = "http://q1.qlogo.cn/g?b=qq&nk={}&s=640"
LOCAL_AVATAR_URL = "./tmp/{}.jpg"
FINAL_IMAGE_URL = "./tmp/{}-final.jpg"
FONT_WIDTH = 20
SMALL_FONT_WIDTH = 13
MAX_LINES = 3
font = ImageFont.truetype("SourceHanSansCN-Medium.otf", FONT_WIDTH, encoding="unic")
font_small = ImageFont.truetype("SourceHanSansCN-Bold.otf", SMALL_FONT_WIDTH, encoding="unic")


def _save_avatar(user_id: int) -> str:
    """
    获取用户头像
    """
    url = AVATAR_URL.format(user_id)
    save_url = LOCAL_AVATAR_URL.format(user_id)
    r = requests.get(url)
    if r.status_code != 200:
        return None
    with open(save_url, "wb") as f:
        f.write(r.content)
    return save_url


# smooth interpolate between 0 and 1
def smooth01(x: float) -> float:
    return math.sin(x * math.pi - math.pi / 2) / 2 + 0.5


# alpha gradient
def alpha_gradient(image: Image, x_s: int, x_e: int) -> Image:
    image = image.convert('RGBA')
    w, h = image.size
    img = Image.new('L', (w, h), 255)
    for x in range(x_s, x_e + 1):
        alpha = 255-int(smooth01((x - x_s)/(x_e - x_s)) * 255)
        tmp_img = Image.new('L', (1, h), alpha)
        img.paste(tmp_img, (x, 0))

    image.putalpha(img)

    return image


def wrap_text(text: str, width: int) -> list:
    """
    先将文本根据\r\n换行再分词换行
    """
    text = text.replace("\r\n", "\n")
    lines = []
    for line in text.split("\n"):
        lines.extend(textwrap.wrap(line, width))
    return lines


def generate(reply: Reply, dump_to='') -> BytesIO:
    """
    生成图片
    """
    avatar_url = _save_avatar(reply.user_id)
    if avatar_url is None:
        raise Exception("avatar not found")
    image = Image.new('RGBA', (560, 150), (0, 0, 0, 255))
    # draw text on the right
    text_wrapped = wrap_text(reply.message, 18)
    y_min = 23
    y_max = 120
    # center vertically
    y_start = (y_max - y_min) / 2 - min(len(text_wrapped), MAX_LINES) * FONT_WIDTH / 2
    y = int(y_start)
    x_start = 165
    x_end = 560
    i = 1
    if len(text_wrapped) > MAX_LINES:
        text_wrapped[MAX_LINES - 1] = text_wrapped[3][:-3] + "..."
    for line in text_wrapped:
        text_size = font.getsize(line)
        # center the text
        x = int(x_start + (x_end - x_start - text_size[0]) / 2)
        with Pilmoji(image, source=MicrosoftEmojiSource) as pilomoji:
            if i > MAX_LINES:
                break
            pilomoji.text((x, y), line, font=font, fill=(255, 255, 255, 255), embedded_color=True)
        y += FONT_WIDTH
        i += 1
    draw = ImageDraw.Draw(image)
    avatar = Image.open(avatar_url)
    avatar = avatar.resize((150, 150))
    avatar = alpha_gradient(avatar, 50, 150)
    # left to right alpha gradient
    # draw avatar on the left
    image.paste(avatar, (0, 0), avatar)

    x_center = 403
    # center user card
    card_size = font_small.getsize("@"+reply.user_card)
    x_card_start = x_center - card_size[0] / 2
    draw.text((x_card_start, 95), "@"+reply.user_card, font=font_small, fill=(169, 172, 184, 255))

    fmt_time = strftime("%Y年%m月%d日 %H点%M分", localtime(reply.time))
    time_size = font_small.getsize(fmt_time)
    x_time_start = x_center - time_size[0] / 2
    draw.text((x_time_start, 115), fmt_time, font=font_small, fill=(169, 172, 184, 255))
    bytes_io = BytesIO()
    image = image.convert('RGB')
    image.save(bytes_io, format="JPEG")
    if len(dump_to) > 0:
        image.save(dump_to)
    return bytes_io
