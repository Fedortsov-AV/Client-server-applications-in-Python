from datetime import datetime
from time import sleep

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy_utils import database_exists, create_database

engine = create_engine('sqlite:///DateBase/serv_db.db3', echo=False, pool_recycle=7200)
if not database_exists(engine.url):
    create_database(engine.url)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    info = Column(Text(250), nullable=True)
    created_on = Column(DateTime(), default=datetime.now())
    history = relationship('UserHistory', backref='users', uselist=False)
    contacts = relationship('UserContact', backref='users')

    def __init__(self, username, info):
        self.username = username
        self.info = info

    def __repr__(self):
        return f'<User({self.username}, {self.info}, {self.created_on})>'


class UserHistory(Base):
    __tablename__ = 'user_history'
    id = Column(Integer(), primary_key=True)
    login_time = Column(DateTime(), default=datetime.now())
    ip_addres = Column(String(15))
    user_id = Column(Integer, ForeignKey('users.id'))
    username = Column(String(50))

    def __init__(self, user_id, ip_addres):
        self.user_id = user_id
        self.ip_addres = ip_addres
        res = session.query(User).filter_by(id=user_id)
        self.username = res[0].username


class UserContact(Base):
    __tablename__ = 'user_contacts'
    id = Column(Integer(), primary_key=True)
    contact = Column(String(50))
    verification = Column(Boolean, default=True)  # для проверки работы default=True, иначе False
    user_id = Column(Integer, ForeignKey('users.id'))


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

if __name__ == '__main__':
    result = session.query(User).filter_by(username='User4')
    print('rows count: ', result.count())
    print('result[0].id: ', result[0].id)
    # user = User('Александр1', "")
    # session.add(user)
    # session.commit()
    history = UserHistory(result[0].id, '127.0.0.1')
    session.add(history)
    session.commit()
