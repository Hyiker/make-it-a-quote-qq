from nonebot import get_driver
from nonebot.log import logger
from .models.model import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import sys


_db_engine = 'sqlite:///db/data.db'
SESSION = None
try:
    engine = create_engine(_db_engine, encoding='utf8',
                           connect_args={'check_same_thread': False},
                           future=True)
    SESSION = sessionmaker(bind=engine)
except Exception as e:
    logger.error('创建数据库连接时失败：{}'.format(e))
    sys.exit(1)


async def get_session():
    return SESSION()


def get_session_sync():
    return SESSION()


@get_driver().on_startup
def db_init():
    logger.info("正在初始化数据库...")
    try:
        with engine.begin() as conn:
            Base.metadata.create_all(engine)
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error('初始化数据库失败：{}'.format(e))
        sys.exit(1)
