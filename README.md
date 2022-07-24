# Twitter的make-it-a-quote机器人qq版本

![example](assets/114514-emoji-multiline-line.jpg)

使用nonebot2+go-cqhttp开发，自动生成makeitaquote卡片的qq机器人（现版本已经加入了很多很多新功能），限定python版本3.9+。

## 部署


项目使用poetry进行包管理，go-cqhttp作为客户端，首先安装poetry然后运行

```bash
poetry install
```

安装依赖。等待依赖安装结束后，项目根目录下创建`bin`和`tmp`两个文件夹、`.env`文件，`.env`文件内容：

```
HOST=127.0.0.1
PORT=11451
COMMAND_START=["/", ""]
LOG_LEVEL=INFO
```

在`bin`文件夹下下载go-cqhttp，更改`config.yml`配置为：

```yml
servers:
  - ws-reverse:
      universal: ws://127.0.0.1:11451/onebot/v11/ws
```

回到项目根目录下执行

```bash
poetry run python main.py
```

启动项目，再根据自己平台不同运行go-cqhttp即可。

其中，“黄鸭”是我的机器人的名字，将其作为关键词使用，可以根据情况修改。

为什么不打docker？懒。

## 生成图片

![多行文本](./assets/114514-multi-line.jpg)

多行文本支持


![单行文本](./assets/114514-single-line.jpg)

单行文本支持


![emoji文本](./assets/114514-emoji-multiline-line.jpg)

emoji文本支持（部分）

## Third Party

- 思源黑体
- 由于数据集、语录涉及各种license问题，请找作者索要
