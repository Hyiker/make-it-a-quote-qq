# coding:utf-8
from dataclasses import dataclass
from nonebot import on_keyword, require
from nonebot.rule import keyword
import pandas as pd
import random
import numpy as np
from bisect import bisect_left
from nonebot.adapters.onebot.v11 import MessageSegment, GroupMessageEvent, Message

gaokao_rule = keyword('我要高考', '高考')
gaokao_cmd = on_keyword(['黄鸭'], rule=gaokao_rule, priority=13)

gaokao = pd.read_csv('gaokao.csv', header=0, encoding='utf-8')

provinces = ['北京', '天津', '辽宁', '吉林', '黑龙江', '上海', '江苏', '浙江', '安徽', '福建', '山东', '湖北', '湖南', '广东', '重庆',
             '四川', '陕西', '甘肃', '河北', '山西', '内蒙古', '河南', '海南', '广西', '贵州', '云南', '西藏', '青海', '宁夏', '新疆', '江西']

# 满分不是750分的省份
not_750 = {'上海': 660, '海南': 900}

bupt_scores = gaokao[gaokao['学校'] == '北京邮电大学']
province_bupt_scores = bupt_scores['平均分数'].tolist()
province_bupt = dict(zip(provinces, province_bupt_scores))


@dataclass
class School:
    score: int
    name: str

    def __lt__(self, other):
        return self.score < other.score

    def __gt__(self, other):
        return self.score > other.score

    def __ge__(self, other):
        return self.score >= other.score

    def __eq__(self, other):
        return self.score == other.score

    def __le__(self, other):
        return self.score <= other.score

    def __repr__(self) -> str:
        return '{}({:.2f})'.format(self.name, self.score)

    def __str__(self) -> str:
        return '{}({:.2f})'.format(self.name, self.score)


province_school_scores = {}
for province in provinces:
    scores = []
    province_df = gaokao[gaokao['招生省份'] == province]
    school_names = province_df['学校'].tolist()
    school_scores = province_df['平均分数'].tolist()
    scores = [School(score, name) for score, name in zip(school_scores, school_names)]
    scores = sorted(scores)
    province_school_scores[province] = scores


def generate_gaokao_score() -> tuple[int, str]:
    province_index = random.randint(0, len(provinces) - 1)
    bupt_score = province_bupt_scores[province_index]
    # 根据bupt_score生成正态分布的高考分数
    mu = bupt_score - 10
    max_score = 750 if province_index not in not_750 else not_750[province_index]
    sigma = (max_score - 20 - mu) / 3.5
    gaokao_score = np.random.normal(mu, sigma, 1)[0]
    gaokao_score = min(max_score, gaokao_score)
    return int(gaokao_score), provinces[province_index]


def find_suitable_school(score: int, province: str) -> list[School]:
    scores = province_school_scores[province]
    # binary search upper bound
    index = bisect_left(scores, School(score, ''))
    return province_school_scores[province][index - 3: index]


scheduler = require('nonebot_plugin_apscheduler').scheduler

gaokao_list = set()


@scheduler.scheduled_job('cron', hour='23', minute='59')
async def clear_gaokaolist():
    gaokao_list.clear()


@gaokao_cmd.handle()
async def gaokao_handler(event: GroupMessageEvent):
    user_id = event.get_user_id()
    group_id = event.group_id
    con = '{}{}'.format(group_id, user_id)
    if con in gaokao_list:
        await gaokao_cmd.finish(Message([MessageSegment.at(user_id), MessageSegment.text('一人每天只能高考一次哦')]))
    gaokao_list.add(con)
    score, province = generate_gaokao_score()
    schools = find_suitable_school(score, province)
    school_names_str = '、'.join([str(school) for school in schools])
    bupt_score = province_bupt[province]
    if len(schools) == 0:
        msg = '重开到了{province}省，高考不负众望地考到了{score}分，收收心该进电子厂了😓'.format(score=score, province=province)
    else:
        msg = '重开到了{province}省，高考不负众望地考到了{score}分，可以读这些学校：\n{schools}。'.format(
            score=score, province=province, schools=school_names_str)
        if score < bupt_score:
            msg += '感觉不如北邮……高考分数……😅'
        else:
            msg += '你给我回来😭'
    await gaokao_cmd.finish(Message([MessageSegment.at(user_id), MessageSegment.text(msg)]))

if __name__ == '__main__':
    sc, pr = generate_gaokao_score()
    print(sc, pr)
    print(find_suitable_school(sc, pr))
