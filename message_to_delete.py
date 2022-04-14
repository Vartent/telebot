from base import Base, Session, engine
import telebot
from sqlalchemy import Column, String, Integer, Date, Boolean
from dotenv import load_dotenv
import os
from os.path import join, dirname
import datetime

bot = telebot.TeleBot("5253553025:AAHgYh1yp19l2YZfl02vEkCNk_YijSpcYDI")


class Message_to_delete(Base):
    __tablename__ = 'message_to_delete'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer)
    user_id = Column(Integer)
    actual = Column(Boolean)
    date = Column(Date)
    steps = Column(Integer)

    def __init__(self, message_id, user_id, steps):
        self.message_id = message_id
        self.user_id = user_id
        self.steps = steps
        self.date = datetime.datetime.today()
        self.actual = True


def delete_after(message, steps):
    session = Session()
    message_to_delete = Message_to_delete(message_id=message.id, user_id=message.chat.id, steps=steps)
    session.add(message_to_delete)
    session.commit()
    session.close()


def check_steps(user_id):
    session = Session()
    messages_to_delete = session.query(Message_to_delete).filter(Message_to_delete.user_id == user_id).all()
    for message_to_delete in messages_to_delete:
        if message_to_delete.date < datetime.date.today() - datetime.timedelta(days=2):
            session.query(Message_to_delete).filter(Message_to_delete.id == message_to_delete.id).delete()
            session.commit()
        elif message_to_delete.steps > 1:
            message_to_delete.steps -= 1
        elif message_to_delete.steps <= 1:
            try:
                session.query(Message_to_delete).filter(Message_to_delete.id == message_to_delete.id).delete()
                session.commit()
                bot.delete_message(chat_id=message_to_delete.user_id, message_id=message_to_delete.message_id)
            except:
                pass
        session.commit()
    session.close()

# Base.metadata.create_all(engine)