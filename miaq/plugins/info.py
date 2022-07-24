# coding: utf-8
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, Event
import tomlkit
from pathlib import Path

txt = Path("pyproject.toml").read_text()
pyproject = tomlkit.parse(txt)
version = pyproject["tool"]["poetry"]["version"]
authors = pyproject["tool"]["poetry"]["authors"]

help_cmd = on_command("help", rule=to_me(), aliases={"帮助", "帮助文档", "文档"}, priority=50)
version_cmd = on_command("version", rule=to_me(), aliases={"版本", "版本号"}, priority=40)
changelog_cmd = on_command("changelog", rule=to_me(), aliases={"更新日志"}, priority=60)

version_text = '''HuangYa (Debian {version}) {version} 20210110
Copyright (C) 2022 Carbene, Personal.
He is free duck; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'''.format(version=version)

help_text = '''黄鸭{version} 试作自动鸭形，由{author}倾情打造
提供makeitaquote、remake、每日一题等服务
组合拳打造产业闭环，实现Q群赋能。'''

changelog_text = '''黄鸭v{version}
添加我要高考的功能'''


@help_cmd.handle()
async def help_cmd_func(event: Event):
    await help_cmd.finish(help_text.format(version=version, author=authors[0]))


@version_cmd.handle()
async def version_cmd_func(event: Event):
    await version_cmd.finish(version_text)


@changelog_cmd.handle()
async def changelog_cmd_func(event: Event):
    await changelog_cmd.finish(changelog_text.format(version=version))
