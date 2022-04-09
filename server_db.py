from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy_utils import database_exists, create_database


# engine = create_engine('sqlite:///DateBase/serv_db.db3', echo=False, pool_recycle=7200, connect_args={'check_same_thread': False})
# if not database_exists(engine.url):
#     create_database(engine.url)


Base = declarative_base()

def init_db(path: str, name: str) -> object:
    engine = create_engine(f'sqlite:///{path}{name}', echo=False, pool_recycle=7200,
                           connect_args={'check_same_thread': False})
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    # print('init_db session ', session)
    return session

# path_bd = 'DateBase/'
# file_name_bd = 'serv_db.db3'
# session = init_db(path_bd, file_name_bd)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    info = Column(Text(250), nullable=True)
    created_on = Column(DateTime(), default=datetime.now())
    online = Column(Boolean, default=0)
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

    def __init__(self, user_id, ip_addres, username):
        self.user_id = user_id
        self.ip_addres = ip_addres
        self.username = username


class UserContact(Base):
    __tablename__ = 'user_contacts'
    id = Column(Integer(), primary_key=True)
    contact = Column(String(50))
    verification = Column(Boolean, default=1)  # для проверки работы default=True, иначе False
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, user_id, contact):
        self.contact = contact
        self.user_id = user_id





# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
# session = Session()

if __name__ == '__main__':
    session = init_db('C:/Users/User/PycharmProjects/Client-server/DateBase/', 'serv_db.db3')
    # print(contact_list("1"))
    # print(add_contact(1, 'User5'))
    contact_list(1)
    # response_user('1', '192.168.1.1')
    # result = session.query(User).filter_by(username='User4')
    # print('rows count: ', result.count())
    # print('result[0].id: ', result[0])
    # cont = UserContact(2, '1')
    # session.add(cont)
    # cont = UserContact(2, 'User4')
    # session.add(cont)
    # session.commit()
    # history = UserHistory(result[0].id, '127.0.0.1')
    # session.add(history)
    # session.commit()
