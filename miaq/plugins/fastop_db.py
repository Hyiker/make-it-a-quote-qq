from sqlalchemy.orm import Session

from .models.model import Group, User, UserCredit, RemakeQueryRecord


def find_or_create_user(user_id: int, session: Session):
    user_db = session.query(User).filter(User.user_id == user_id).one_or_none()
    if user_db is None:
        session.add(User(user_id=user_id))
        session.commit()
        user_db = session.query(User).filter(User.user_id == user_id).one()
    return user_db


def find_or_create_user_credit(user_id: int, session: Session):
    user_credit = session.query(UserCredit).filter(UserCredit.user_id == user_id).one_or_none()
    if user_credit is None:
        session.add(UserCredit(user_id=user_id))
        session.commit()
        user_credit = session.query(UserCredit).filter(UserCredit.user_id == user_id).one()
    return user_credit


def find_or_create_group(group_id: int, session: Session):
    group_db = session.query(Group).filter(Group.group_id == group_id).one_or_none()
    if group_db is None:
        session.add(Group(group_id=group_id))
        session.commit()
        group_db = session.query(Group).filter(Group.group_id == group_id).one()
    return group_db


def find_or_create_remake_query(user_id: int, group_id: int, session: Session):
    remake_query = session.query(RemakeQueryRecord)\
        .filter(RemakeQueryRecord.user_id == user_id, RemakeQueryRecord.group_id == group_id).one_or_none()
    if remake_query is None:
        session.add(RemakeQueryRecord(user_id=user_id, group_id=group_id))
        session.commit()
        remake_query = session.query(RemakeQueryRecord).filter(RemakeQueryRecord.user_id ==
                                                               user_id, RemakeQueryRecord.group_id == group_id).one()
    return remake_query
