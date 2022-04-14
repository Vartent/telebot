from base import Base, Session, engine
import telebot
from sqlalchemy import Column, String, Integer, Date, Boolean
from dotenv import load_dotenv
import os
from os.path import join, dirname


def get_from_ev(key):
    dotenv_path = join(dirname(__file__), 'dialog_messages.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key)


bot = telebot.TeleBot("5253553025:AAHgYh1yp19l2YZfl02vEkCNk_YijSpcYDI")



class Users(Base):

    __tablename__ = 'users'


    id = Column(Integer, primary_key=True)
    name = Column(String)
    lastname = Column(String)
    middlename = Column(String)
    position = Column(String)
    departament = Column(String)
    email = Column(String)
    email_pass = Column(String)
    phone = Column(String)
    access = Column(Integer)
    state = Column(Integer)

    def __init__(self, id):
        self.id = id
        self.name = None
        self.lastname = None
        self.middlename = None
        self.position = None
        self.departament = None
        self.email = None
        self.email_pass = None
        self.phone = None
        self.access = 1
        self.state = None

def get_info_from_message(message, state):
    session = Session()
    user = session.query(Users).filter(Users.id == message.chat.id).first()
    attr = state[(state.index("_attr") + 5):]
    setattr(user, attr, message.text)
    session.commit()




# Base.metadata.create_all(engine)