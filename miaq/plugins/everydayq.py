# -*- coding: utf-8 -*-
from nonebot import logger, on_keyword, require
from nonebot.rule import keyword
from nonebot.adapters.onebot.v11 import MessageSegment, Message, GroupMessageEvent
from nonebot.adapters.onebot.exception import ActionFailed
from datetime import datetime, timedelta
import re

from .models.model import AnswerRecord

from .fastop_db import find_or_create_group, find_or_create_user_credit
from .parse_questions import read_questions
from nonebot.params import Depends
from nonebot.log import logger
from sqlalchemy.orm import Session
from .init_db import get_session


everyday_question_rule = keyword('每日一题')
everyday_answer_rule = keyword('答案')
everyday_credit_rule = keyword('查询积分')

everyday_credit = on_keyword(["黄鸭"], rule=everyday_credit_rule, priority=3)
everyday_question = on_keyword(["黄鸭"], rule=everyday_question_rule, priority=2)
everyday_answer = on_keyword(["黄鸭"], rule=everyday_answer_rule, priority=1)

questions = read_questions('questions.txt')
credit_add = 10
group_freq = {}

scheduler = require('nonebot_plugin_apscheduler').scheduler


@scheduler.scheduled_job('cron', hour='23', minute='59')
async def update_question():
    global questions
    questions = read_questions('questions.txt')


@scheduler.scheduled_job('cron', hour='0', minute='0')
async def clear_all():
    session = get_session()
    # update group.qid +=1, group.answered = False
    for ar in session.query(AnswerRecord):
        ar.answered = False
        ar.qid = ar.qid + 1
    session.commit()
    session.close()
    group_freq.clear()


def compute_qid(qid: int, group_id: int) -> int:
    return (qid + group_id + 1919810) % len(questions)


@everyday_question.handle()
async def question(event: GroupMessageEvent, session: Session = Depends(get_session)):
    group_id = event.group_id
    group = find_or_create_group(group_id, session)
    # 5 minutes after the question
    if group_id in group_freq and datetime.now() - group_freq[group_id] < timedelta(minutes=20):
        await everyday_question.finish('题目的获取间隔是二十分钟哦')
    elif group.answered:
        ar = session.query(AnswerRecord).filter(AnswerRecord.group_id == group_id,
                                                AnswerRecord.time >= datetime.now().date(),
                                                AnswerRecord.time < datetime.now().date() + timedelta(days=1)).all()
        if len(ar) == 0:
            group.answered = False
            session.commit()
        else:
            await everyday_question.finish('今天的每日一题已经被{}AC了哦'.format(ar[0].user_nickname))
    group_freq[group_id] = datetime.now()
    q = questions[compute_qid(group.qid, group_id)]
    msg = '{}\n{}\n每日一题一人只能回答一次，回答正确奖励{}积分，回复例：黄鸭 答案A'.format(q.question, '\n'.join(q.options), credit_add)
    try:
        await everyday_question.finish(msg)
    except ActionFailed:
        # split msg in half
        msg_len = len(msg)
        msg_half = msg_len // 2
        msg_half_1 = msg[:msg_half]
        msg_half_2 = msg[msg_half:]
        await everyday_question.send(msg_half_1)
        await everyday_question.finish(msg_half_2)


def extract_answer_from_text(plain_text: str) -> str:
    # extract first sequent alphabetical word from plain_text
    alphabetic_regex = r'[a-zA-Z]+'
    match = re.search(alphabetic_regex, plain_text)
    if match is None:
        return ''
    return match.group(0).lower()


@everyday_answer.handle()
async def answer(event: GroupMessageEvent, session: Session = Depends(get_session)):
    group_id = event.group_id
    group = find_or_create_group(group_id, session)
    user_id = event.get_user_id()
    user_name = ''
    try:
        user_name = event.dict()['sender']['card']
        if not user_name:
            user_name = event.dict()['sender']['nickname']
    except KeyError:
        user_name = user_id
    if group.answered:
        ar = session.query(AnswerRecord).filter(AnswerRecord.group_id == group_id,
                                                AnswerRecord.time >= datetime.now().date(),
                                                AnswerRecord.time < datetime.now().date() + timedelta(days=1)).all()
        await everyday_question.finish('今天的每日一题已经被{}A了哦'.format(ar[0].user_nickname))
    ua = session.query(AnswerRecord).filter(AnswerRecord.group_id == group_id,
                                            AnswerRecord.user_id == user_id,
                                            AnswerRecord.corrected == True,
                                            AnswerRecord.time >= datetime.now().date(),
                                            AnswerRecord.time < datetime.now().date() + timedelta(days=1)).one_or_none()
    if ua is not None:
        await everyday_answer.finish(Message([MessageSegment.at(user_id),
                                              '你今天已经答过题了哦']))

    q = questions[compute_qid(group.qid, group_id)]
    text = event.get_plaintext()
    answer = extract_answer_from_text(text)
    corrected = answer == q.answer
    logger.info('{}, {}'.format(answer, q.answer))
    answer_record = AnswerRecord(group_id=group_id, user_id=user_id,
                                 user_nickname=user_name, answer=answer,
                                 time=datetime.now(), qid=group.qid, corrected=corrected)
    session.add(answer_record)
    session.commit()
    if corrected:
        group.answered = True
        # truncate analysis to 50 characters
        if len(q.analysis) > 50:
            analysis = q.analysis[:50] + '...'
        else:
            analysis = q.analysis
        user = find_or_create_user_credit(user_id, session)
        user.credit += credit_add
        session.commit()
        await everyday_answer.finish('回答正确，{}的积分更新为{}\n{}'.format(user_name,
                                                                  user.credit, analysis))
    else:
        await everyday_answer.finish('回答错误！')


@everyday_credit.handle()
async def credit(event: GroupMessageEvent, session: Session = Depends(get_session)):
    user_id = event.get_user_id()
    user = find_or_create_user_credit(user_id, session)
    await everyday_credit.finish(Message([MessageSegment.at(user_id), '的积分是{}'.format(user.credit)]))
