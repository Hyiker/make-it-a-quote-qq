# coding:utf-8
from textwrap import fill
from typing import final
import requests
from io import BytesIO
from pilmoji import Pilmoji
from pilmoji.source import MicrosoftEmojiSource
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from time import time
import math
import textwrap

AVATAR_URL = "http://q1.qlogo.cn/g?b=qq&nk={}&s=640"
LOCAL_AVATAR_URL = "./tmp/{}.jpg"
FINAL_IMAGE_URL = "./tmp/{}-final.jpg"
FONT_WIDHT = 20
font = ImageFont.truetype("SourceHanSansCN-Medium.otf", FONT_WIDHT, encoding="unic")
font_small = ImageFont.truetype("SourceHanSansCN-Bold.otf", 13, encoding="unic")


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


def generate(user_id: int, user_card: str, text: str, debug=False) -> BytesIO:
    """
    生成图片
    """
    avatar_url = _save_avatar(user_id)
    if avatar_url is None:
        raise Exception("avatar not found")
    image = Image.new('RGBA', (560, 150), (0, 0, 0, 255))
    # draw text on the right
    text_wrapped = textwrap.wrap(text, width=18)
    y = 23
    i = 1
    for line in text_wrapped:
        with Pilmoji(image, source=MicrosoftEmojiSource) as pilomoji:
            if i >= 4:
                pilomoji.text((165, y), '...', font=font, fill=(255, 255, 255, 255), embedded_color=True)
                break
            pilomoji.text((165, y), line, font=font, fill=(255, 255, 255, 255), embedded_color=True)
        y += FONT_WIDHT
        i += 1
    draw = ImageDraw.Draw(image)
    avatar = Image.open(avatar_url)
    avatar = avatar.resize((150, 150))
    avatar = alpha_gradient(avatar, 50, 150)
    # left to right alpha gradient
    # draw avatar on the left
    image.paste(avatar, (0, 0), avatar)

    draw.text((380, 110), "@"+user_card, font=font_small, fill=(169, 172, 184, 255))
    bytes_io = BytesIO()
    image = image.convert('RGB')
    image.save(bytes_io, format="JPEG")
    if debug:
        image.save(FINAL_IMAGE_URL.format(user_id))
    return bytes_io


if __name__ == "__main__":
    generate(114514, "卑微的甲醛", "什么年代，还在骑传统单车都什么年代，还在骑传统单车都什么年代，还在骑传统单车都什么年代，还在骑传统单车都什么年代，还在骑传统单车都什么年代", True)
