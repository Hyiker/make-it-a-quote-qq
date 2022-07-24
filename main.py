import nonebot
from nonebot.adapters.onebot.v11.adapter import Adapter as OBV11Adapter
from os import path

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(OBV11Adapter)

nonebot.load_plugins('miaq/plugins')

if __name__ == '__main__':
    nonebot.run()
