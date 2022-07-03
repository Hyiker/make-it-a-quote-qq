from miaq.plugins.generate_image import generate
from miaq.plugins.reply import Reply
from time import time
if __name__ == "__main__":
    generate(Reply(114514, "卑微的甲醛卑微的甲醛卑微的甲醛卑微的甲醛",
             "什么年代，还在骑传统单车都\r\n什么年代，还在骑传统单车都什么年代，还在骑传统单车都什么年代，还在骑传统单车都什么年代，还在骑传统单车都什么年代", int(time())), 'tmp/114514-multi-line.jpg')

    generate(Reply(114514, "卑微的甲醛卑微的甲醛卑微的甲醛卑微的甲醛",
             "什么年代，还在抽传统香烟", int(time())), 'tmp/114514-single-line.jpg')

    generate(Reply(114514, "甲醛捏",
             "💈\r\n🐢", int(time())), 'tmp/114514-emoji-multiline-line.jpg')
