from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Sequence
Base = declarative_base()


class UserCredit(Base):
    __tablename__ = 'user_credit'
    user_id = Column(Integer, primary_key=True, nullable=False, index=True, unique=True)
    credit = Column(Integer, nullable=False, default=0)


class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, nullable=False, index=True, unique=True)
    refreshable_remake_count = Column(Integer, nullable=False, default=1)


class RemakeRecord(Base):
    __tablename__ = "remake_record"
    id = Column(Integer, Sequence('plugin_id_seq'), primary_key=True, nullable=False, index=True, unique=True)
    user_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)
    country_json = Column(Text, nullable=False)
    time = Column(DateTime, nullable=False)


class RemakeQueryRecord(Base):
    __tablename__ = "remake_query_record"
    user_id = Column(Integer, primary_key=True, nullable=False)
    group_id = Column(Integer, primary_key=True, nullable=False)
    queried = Column(Boolean, nullable=False, default=False)
    __table_args__ = (
        UniqueConstraint('user_id', 'group_id'),
    )


class Group(Base):
    __tablename__ = 'group'
    group_id = Column(Integer, primary_key=True, nullable=False, index=True, unique=True)
    answered = Column(Boolean, nullable=False, default=False)
    qid = Column(Integer, nullable=False, default=0)


class AnswerRecord(Base):
    __tablename__ = 'answer_record'
    id = Column(Integer, Sequence('plugin_id_seq'), primary_key=True, nullable=False, index=True, unique=True)
    group_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    user_nickname = Column(String(80), nullable=False)
    time = Column(DateTime, nullable=False)
    qid = Column(Integer, nullable=False)
    answer = Column(String, nullable=False)
    corrected = Column(Boolean, nullable=False, default=False)
