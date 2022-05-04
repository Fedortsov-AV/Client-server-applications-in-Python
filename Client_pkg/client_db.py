"""В данном модуле формируется БД клиента"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database


def init_db(name: str, path: str):
    """Функция инициализирующая сессию клиента."""

    engine = create_engine(f'sqlite:///{path}client_db_{name}.db3', echo=False, pool_recycle=7200,
                           connect_args={'check_same_thread': False})
    if not database_exists(engine.url):
        create_database(engine.url)
    # Base.metadata.drop_all(bind=engine, tables=[UserContact.__table__])
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


Base = declarative_base()


class MessageHistory(Base):
    """Класс создает таблицу 'message_history'.
    Для создания экземпляра класса в конструктор необходимо передать
    MessageHistory(имя_отправителя (str), имя получателя(str), текст_сообщения(str))"""

    __tablename__ = 'message_history'
    id = Column(Integer, primary_key=True)
    msg_to = Column(String(20), nullable=False)
    msg_from = Column(String(20), nullable=False)
    text_message = Column(Text(255))
    create_time = Column(DateTime(), default=datetime.now())
    readed = Column(Boolean, default=0)

    def __init__(self, msg_to: str, msg_from: str, text_message: str):
        self.msg_to = msg_to
        self.msg_from = msg_from
        self.text_message = text_message


class UserContact(Base):
    """Класс создает таблицу 'user_contacts'.
    Для создания экземпляра класса в конструктор необходимо передать
    UserContact(имя_контакта (str), первый_блок_открытого_ключа(str), второй_блок_открытого_ключа(str), третий_блок_открытого_ключа(str))
    Обратите внимание, блоки открыто ключа должны иметь тип *string*"""

    __tablename__ = 'user_contacts'
    id = Column(Integer(), primary_key=True)
    contact = Column(String(20))
    open_key_y = Column(Text)
    open_key_g = Column(Text)
    open_key_p = Column(Text)
    verification = Column(Boolean, default=1)  # для проверки работы default=True, иначе False

    def __init__(self, contact: str, open_key_y: str, open_key_g: str, open_key_p: str):
        self.contact = contact
        self.open_key_y = open_key_y
        self.open_key_g = open_key_g
        self.open_key_p = open_key_p


if __name__ == '__main__':
    pass
