from sqlalchemy import Column, String, Integer, Date, Boolean, ForeignKey
from base import Base, Session, engine
from datetime import date
import telebot
from telebot import types
import json
import tasks
from setup import session_dec
import uuid

#switch to next user function required

admin_id = 180193472

class Task_queue(Base):
    __tablename__ = 'task_queue'

    prim_id = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String)
    queue = Column(String) #users in line
    current_user = Column(Integer) #current user index in queue solving task
    task_child = Column(String)

    def __init__(self, queue: str):
        while True:
            try:
                self.id = str(uuid.uuid4())
                break
            except:
                print('error compiling id')
        self.queue = queue
        self.current_user = 0
        self.task_child = ""

    def list_to_string(self, l: list):
        return '\n'.join(l)

    def string_to_list(self, string: str):
        return string.split()

    def string_to_tuple(self, string: str):
        return string.splitlines()

    def type_id(self):
        try:
            d = json.dumps({'type': 'queue',
                          'id': self.id})
        except Exception as e:
            print(e.args)
        return json.dumps({'type': 'queue',
                           'id': self.id})

    def store_queue(self, l):
        self.queue = self.list_to_string(l)

    def get_current_user(self):
        return self.string_to_tuple(self.queue)[self.current_index]

    def create_task(self, title, duration=1):
        task = tasks.Task(title, duration=duration, parent_info=self.type_id(), slave_id=self.get_current_user())
        self.task_child = json.dumps({'type': 'task',
                                      'id': task.id})
        return task

    def queue_task(self, title, duration=1):
        session = Session()
        print('session:', session)
        task = self.create_task(title, duration)
        print('task:', task)
        session.add(task)
        session.commit()

    def next_curr(self):
        self.current_index += 1
        return self.current_index

    def get_next_user(self):
        self.next_curr()
        return self.get_current_user()

    def switch_task_user_next(self):
        session = Session()
        task = session.query(tasks.Task).filter(tasks.Task.id == json.loads(self.task_child)["id"]).first()
        task.slave_id = self.get_next_user()
        session.commit()

    def get_task_from_bd(self):
        session = Session()
        print(session)
        return session.query(tasks.Task).filter(tasks.Task.id == json.loads(self.task_child)["id"]).first()

    def send_task_next_user(self):
        self.switch_task_user_next()
        task = self.get_task_from_bd()
        return task.send_task()

def get_queue_of_task(task_id) -> Task_queue:
    session = Session()
    task_ids = session.query(tasks.Task.id).all()
    task = session.query(tasks.Task).filter(tasks.Task.id == task_id).first()
    queue_id = json.loads(task.parent)["id"]
    queue = session.query(Task_queue).filter(Task_queue.id == queue_id).first()
    return queue

def create_test_queue():
    session = Session()
    queue = Task_queue(queue=f'{admin_id} {admin_id}')
    print('queue_id:', queue.id)
    session.add(queue)
    session.flush()
    q = queue
    session.commit()
    session.close()
    return q

def create_test_task(session=None):

    queue = create_test_queue()
    task = queue.create_task(title='Hello World!', session=session)
    return task


Base.metadata.create_all(engine)