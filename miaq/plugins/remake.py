# -*- coding: utf-8 -*-
from nonebot import get_driver
from dataclasses import dataclass
from nonebot import on_keyword
from nonebot.rule import keyword
from nonebot.params import Depends
from nonebot.log import logger
from sqlalchemy.orm import Session
from sqlalchemy import update
import pandas as pd
from nonebot.adapters.onebot.v11 import MessageSegment, GroupMessageEvent, Message
import random
import requests

from .fastop_db import find_or_create_remake_query, find_or_create_user, find_or_create_user_credit
from .init_db import get_session, engine, get_session_sync
from .models.model import RemakeQueryRecord, RemakeRecord, User
from nonebot import require
from datetime import datetime
import json

scheduler = require('nonebot_plugin_apscheduler').scheduler


reply_rule = keyword('remake', '瑞美', '蕊魅', '瑞梅')

remake = on_keyword(["黄鸭"], rule=reply_rule, priority=10)

remake_query_rule = keyword('数据', '记录')
remake_query = on_keyword(['黄鸭'], rule=remake_query_rule, priority=7)


remake_rank_rule = keyword('rank', '排名')
remake_rank = on_keyword(['黄鸭'], rule=remake_rank_rule, priority=8)

credit_cost = 10


@dataclass
class Country:
    name: str
    population: int
    gini: float
    area: int
    region: str
    gdp: float = -1


country_cache = {}

countries = pd.read_csv("population.csv", header=0)
gdps = pd.read_csv("gdp.csv", header=0).fillna(-1)
gdp_table = dict(zip(gdps['Country Code'].to_list(), gdps['2021'].to_list()))
country_names = countries['Country'].tolist()
country_codes = countries['Country code'].tolist()
country_population = countries['2020'].tolist()
world_population = int(countries['2020'].sum())


async def random_choose_country(retry=True) -> Country:
    # choose a random country with weighted with population
    country_index = random.choices(range(len(country_names)), weights=country_population, k=1)[0]
    country_name = country_names[country_index]
    country_code = country_codes[country_index]
    if country_name in country_cache:
        return country_cache[country_name]
    try:
        response = requests.get("https://restcountries.com/v3.1/alpha/{}".format(country_code))
        if response.status_code == 404:
            response = requests.get("https://restcountries.com/v3.1/name/{}".format(country_name))
        if response.status_code != 200:
            return Country("", country_population[country_index], 0, 0, "")
        result = response.json()[0]
        gini = '未知'
        if 'gini' in result and len(list(result['gini'].keys())):
            gini = result['gini'][list(result['gini'].keys())[0]]
        try:
            if 'zho' in result['translations']:
                country_name_cn = result['translations']['zho']['common']
            else:
                country_name_cn = result['name']['nativeName']['zho']['common']
        except KeyError:
            country_name_cn = country_name
        country_code = result['cca3']
        if country_code in gdp_table:
            gdp = gdp_table[country_code]
        else:
            gdp = -1
        region = result['region']
        if region == 'Americas':
            region = result['subregion']
        c = Country(country_name_cn, country_population[country_index], gini, result['area'], region, gdp)
        country_cache[country_name] = c
        return c
    except Exception as e:
        logger.error(e)
        if retry:
            return await random_choose_country(retry=False)
        return Country("", 0, 0, 0, "")

reaction_list = {
    '中国': '十循种花家了捏🤭🤭🤭',
    '美国': '你给我回来😭😭😭',
    '日本': '罕见去当本子了是吧😠😠😠',
    '韩国': '罕见去当棒子了是吧😠😠😠',
    'Europe': '你给我回来😭😭😭',
    '印度': '这下阿三了🤗🤗🤗',
    '朝鲜': '可不敢乱说😰😰😰',
    '越南': '可不敢乱说😰😰😰',
    'Africa': '哼，想逃？🤗🤗🤗',
    'Australia': '你给我回来😭😭😭',
}


def get_reaction(country: Country) -> str:
    if country.name in reaction_list:
        return reaction_list[country.name]
    if country.region in reaction_list:
        return reaction_list[country.region]
    return ''


def translate_region(region_en: str) -> str:
    if region_en == 'Africa':
        return '非洲'
    elif region_en == 'Asia':
        return '亚洲'
    elif region_en == 'Europe':
        return '欧洲'
    elif region_en == '"North America"':
        return '北美洲'
    elif region_en == '"South America"':
        return '南美洲'
    elif region_en == 'Oceania':
        return '大洋洲'
    elif region_en == 'Antarctica':
        return '南极洲'
    else:
        return region_en


# clear remake_list at 00:00 and 12:00
@scheduler.scheduled_job('cron', hour='0,12', minute='1')
async def clear_remake_list():
    session = await get_session()
    logger.info("refreshing")
    session.execute(update(User).values(refreshable_remake_count=1))
    session.commit()
    session.close()


@remake.handle()
async def handle_first_receive(event: GroupMessageEvent, session: Session = Depends(get_session)):
    # get username
    user_id = event.get_user_id()
    group_id = event.group_id
    at = MessageSegment.at(user_id)
    user_db = find_or_create_user(user_id, session)
    if user_db.refreshable_remake_count <= 0:
        user_credit = find_or_create_user_credit(user_id, session)
        if user_credit.credit >= credit_cost:
            user_credit.credit -= credit_cost
            session.commit()
            await remake.send(Message([at, "消耗{}点积分，剩余{}，正在remake中...".format(credit_cost, user_credit.credit)]))
        else:
            await remake.finish(Message([at, MessageSegment.text('每天0点和12点赠送remake1次，当前积分{}，无法remake，打个🦶休息下吧'.format(user_credit.credit))]))
    else:
        await remake.send(Message([at, "正在remake中..."]))
        stmt = update(User).where(User.user_id == user_id).values(
            refreshable_remake_count=user_db.refreshable_remake_count - 1)
        session.execute(stmt)
        session.commit()
    country = await random_choose_country()
    country_json = {
        'name': country.name,
        'population': country.population,
        'gini': country.gini,
        'area': country.area,
        'region': country.region,
        'gdp': country.gdp,
    }
    session.add(RemakeRecord(user_id=user_id, group_id=group_id, country_json=json.dumps(
        country_json, separators=(',', ':')), time=datetime.now()))
    session.commit()
    if len(country.name) == 0:
        await remake.finish(Message([at, MessageSegment.text('以{:.6}%的概率重开到了黄鸭查不到的一个不知名小国，毁灭吧（无感情）'.format(country.population * 100 / world_population))]))
    reaction = get_reaction(country)
    gdp_text = '，年人均GDP{:.2f}人民币'.format(country.gdp * 6.75) if country.gdp != -1 else ''
    msg = Message([at, MessageSegment.text("以{:.4}%的概率重开到了{}，位于{}{}。{}".format(country.population * 100 / world_population,
                                                                               country.name, translate_region(
                                                                                   country.region), gdp_text, reaction))])
    await remake.finish(msg)

remake_query_text = '''本群共remake{remake_all}次，你在其中贡献{user_remake}次，你remake的平均GDP为{user_remake_gdp:.2f}人民币。'''


@scheduler.scheduled_job('cron', hour='23', minute='59')
async def update_query():
    session = get_session()
    rqq = session.query(RemakeRecord).all()
    for rq in rqq:
        rq.queried = False
    session.commit()
    session.close()


@remake_query.handle()
async def handle_remake_query(event: GroupMessageEvent, session: Session = Depends(get_session)):
    group_id = event.group_id
    user_id = event.get_user_id()
    rq = find_or_create_remake_query(user_id, group_id, session)
    if rq.queried:
        await remake_query.finish(Message([MessageSegment.at(user_id),
                                           MessageSegment.text('一人一天只能查询一次remake数据🤯')]))
    rq.queried = True
    session.commit()
    user_remake = session.query(RemakeRecord).filter(RemakeRecord.group_id ==
                                                     group_id, RemakeRecord.user_id == user_id).all()
    remake_all = session.query(RemakeRecord).filter(RemakeRecord.group_id == group_id).count()

    if len(user_remake) == 0:
        await remake_query.finish(Message([MessageSegment.at(user_id),
                                           MessageSegment.text('你还没有remake过哦')]))
    gdp_avg = 0
    gdp_count = 0
    for rm in user_remake:
        gdp = json.loads(rm.country_json)['gdp']
        if gdp != -1:
            gdp_avg += gdp
            gdp_count += 1
    if gdp_count == 0:
        gdp_avg = 0
    else:
        gdp_avg = gdp_avg / gdp_count
    await remake_query.finish(Message([MessageSegment.at(user_id), MessageSegment.text(remake_query_text.format(
        user_remake_gdp=gdp_avg,
        user_remake=len(user_remake),
        remake_all=remake_all
    ))]))


@dataclass
class RemakeRank:
    user_id: int
    times: int
    gdp_sum: float
    gdp_valid: int
    time_rank: int
    gdp_rank: int


group_remake = {}


@scheduler.scheduled_job('cron', hour='*', minute='0')
async def gr():
    group_remake.clear()
    session = get_session_sync()
    rr = session.query(RemakeRecord).all()
    for record in rr:
        group_id = record.group_id
        if group_id not in group_remake:
            group_remake[group_id] = {}
        user_id = record.user_id
        gdp = json.loads(record.country_json)['gdp']
        if user_id not in group_remake[group_id]:
            group_remake[group_id][user_id] = RemakeRank(user_id, 1, 0 if gdp < 0 else gdp,
                                                         1 if gdp > 0 else 0, -1, -1)
        else:
            group_remake[group_id][user_id].times += 1
            group_remake[group_id][user_id].gdp_sum += gdp if gdp > 0 else 0
            group_remake[group_id][user_id].gdp_valid += 1 if gdp > 0 else 0
    for group_id in group_remake:
        users = list(group_remake[group_id].values())
        users_sorted_by_times = sorted(users, key=lambda x: x.times, reverse=True)
        users_sorted_by_gdp = sorted(users, key=lambda x: x.gdp_sum /
                                     float(max(x.gdp_valid, 1)), reverse=True)
        for i, user in enumerate(users_sorted_by_times):
            user.time_rank = i + 1
        for i, user in enumerate(users_sorted_by_gdp):
            user.gdp_rank = i + 1
    session.close()
driver = get_driver()


@driver.on_bot_connect
async def do_something():
    await gr()

remake_rank_text = '''你的remake次数排名为{time_rank}/{total_time}，你的remake平均GDP排名为{gdp_rank}/{total_gdp}'''


@remake_rank.handle()
async def handle_remake_rank(event: GroupMessageEvent, session: Session = Depends(get_session)):
    group_id = event.group_id
    user_id = event.get_user_id()
    uid = int(user_id)
    gid = int(group_id)
    try:
        text = remake_rank_text.format(
            time_rank=group_remake[gid][uid].time_rank,
            total_time=len(group_remake[gid]),
            gdp_rank=group_remake[gid][uid].gdp_rank,
            total_gdp=len(group_remake[gid])
        )
    except KeyError as e:
        text = 'remake排名每小时刷新一次，你在这之前还没有remake过哦'
        logger.error(e)
    await remake_rank.finish(Message([MessageSegment.at(user_id), MessageSegment.text(text)]))
