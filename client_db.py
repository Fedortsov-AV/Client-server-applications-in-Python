from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database


from common.variables import USER_NAME

def init_db(name):
    engine = create_engine(f'sqlite:///DateBase/client_db_{name}.db3', echo=False, pool_recycle=7200, connect_args={'check_same_thread': False})
    if not database_exists(engine.url):
        create_database(engine.url)
    # Base.metadata.drop_all(bind=engine, tables=[UserContact.__table__])
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

Base = declarative_base()


class MessageHistory(Base):
    __tablename__ = 'message_history'
    id = Column(Integer, primary_key=True)
    msg_to = Column(String(20), nullable=False)
    msg_from = Column(String(20), nullable=False)
    text_message = Column(Text(255))
    create_time = Column(DateTime(), default=datetime.now())
    readed = Column(Boolean, default=0)

    def __init__(self, msg_to, msg_from, text_message):
        self.msg_to = msg_to
        self.msg_from = msg_from
        self.text_message = text_message


class UserContact(Base):
    __tablename__ = 'user_contacts'
    id = Column(Integer(), primary_key=True)
    contact = Column(String(20))
    verification = Column(Boolean, default=1)  # для проверки работы default=True, иначе False

    def __init__(self, contact):
        self.contact = contact




if __name__ == '__main__':
    pass
