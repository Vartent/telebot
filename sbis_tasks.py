from base import Base, Session, engine
import telebot
from sqlalchemy import Column, String, Integer, Date, Boolean
from dotenv import load_dotenv
import os
from os.path import join, dirname


class Sbis_tasks(Base):

    __tablename__ = 'sbis_tasks'

    id = Column(String)
    date = Column(Date)
    num = Column(Integer)
    deadline_date = Column(Date)
    deadline_time = Column(Date) #time till deadline\СРОК
    responsible_lastname = Column(String)
    responsible_name = Column(String)
    responsible_middlename = Column(String)
    author_lastname = Column(String)
    author_name = Column(String)
    author_middlename = Column(String)
    attachment_id = Column(String)
    attachment_link = Column(String)
