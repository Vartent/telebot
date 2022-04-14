from sqlalchemy import Column, String, Integer, Date, Boolean, DateTime
from base import Base, engine
import datetime
from telebot import types
from setup import session_dec
import uuid

# engine.execute('ALTER TABLE tasks ADD COLUMN deadline DATE')

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(String, primary_key=True)
    title = Column(String)
    creation_date = Column(Date)
    duration = Column(DateTime)
    slave_id = Column(Integer)
    state = Column(String)
    parent = Column(String)
    additions = Column(String)
    deadline = Column(Date)

    def __init__(self, title, duration: int, parent_info: str, slave_id, additions=''):
        while True:
            try:
                self.id = str(uuid.uuid4())
                break
            except:
                print('error compiling id')
        self.title = title
        self.creation_date = datetime.date.today()
        self.duration = datetime.timedelta(days=duration)
        self.parent = parent_info
        self.slave_id = slave_id
        self.state = 'processing'
        self.additions = additions
        self.deadline = self.creation_date + self.duration

    def add_addition(self, path: str, session=None):
        self.additions += path + "\n"

    def task_keyboard(self):
        keyboard = types.InlineKeyboardMarkup()
        butt_complete = types.InlineKeyboardButton(text="Выполнено", callback_data=f"task_complete_{self.id}")
        butt_incomplete = types.InlineKeyboardButton(text="Не выполнено", callback_data=f"task_incomplete_{self.id}")
        butt_get_additions = types.InlineKeyboardButton(text=f"Приложить документы",
                                                        callback_data=f"get_addition_{self.id}")
        butt_send_additions = types.InlineKeyboardButton(text="Показать приложения",
                                                         callback_data=f"send_addition_{self.id}")
        keyboard.row(butt_complete, butt_incomplete)
        keyboard.row(butt_get_additions)
        keyboard.row(butt_send_additions)
        return keyboard

    def task_message(self):
        addition_text = lambda adds: "0" if adds == "" or adds == None else f"Документов: {len(adds.splitlines())}"
        text = f"Задача №{self.id}:\n{self.title} \n в срок до:{self.deadline}\n\n"\
               f"Документов приложено: {addition_text(self.additions)}"
        return text
    #check if text will bbe like "Документов приложено: Документов" when its 0 attachments there

    def send_task(self):
        return self.slave_id, self.task_message(), self.task_keyboard()

