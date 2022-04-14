from flask import Flask, request
import os
import telebot
from base import Session
from telebot import types
from users import Users, get_from_ev
from config import states, reg_attr, URL
import threading
from message_to_delete import delete_after, check_steps
import time
import tasks
import task_queue
import glob
# !!! add attachments to regular task


admin_id = 180193472
token = "5253553025:AAHgYh1yp19l2YZfl02vEkCNk_YijSpcYDI"
bot = telebot.TeleBot(token)
app = Flask(__name__)
bot.set_webhook(URL)


@app.route('/', methods=['POST']) # localhost:5000/ - на этот адрес телеграм шлет свои сообщения через тунель
def operate():
    '''
    Gets a POST JSON request with message data.

    :return: a message object for handlers to work with
    '''
    global update
    global request_body_dict
    request_body_dict = request.json
    try:
        add_user(int(request_body_dict['message']['chat']['id']))
    except:
        pass
    try:
        if 'message' in request_body_dict.keys():
            check_steps(int(request_body_dict['message']['chat']['id']))
        elif 'callback_query' in request_body_dict.keys():
            check_steps(int(request_body_dict['callback_query']['message']['chat']['id']))
    except:
        pass
    update = telebot.types.Update.de_json(request_body_dict)
    bot.process_new_updates([update])
    time.sleep(0.5)
    return {"ok": True}


#DECORATOR session creating
def session_dec(func):
    '''
    decorator for methods working with SqlAlchemy database.
    Creates new session before and commits it after changes are applied.

    :param func:
    '''

    def wraper(*args, **kwargs):
        session = Session(autoflush=False)
        func(session=session, *args, **kwargs)
        session.commit()
        session.close()
    return wraper


@session_dec
def add_user(id, session=None):
    '''
    Adding new user to users table database by its telegram id
    other parameters of a user are set to None
    
    :param id:
    :param session:
    '''

    if len(session.query(Users).filter(Users.id == id).all()) == 0:
        session.add(Users(id))
        greetings_message = bot.send_message(id, get_from_ev('GREETINGS'))
        delete_after(greetings_message, 1)

@session_dec
def remove_user(user_id=None, session=None):
    '''
    Deletes existing user. Else: false

    :param id:
    :param session:
    '''
    try:
        session.query(Users).filter(Users.id == user_id).delete()
    except:
        print('user_id required')



#regestraition block
@bot.message_handler(commands='reg')
@session_dec
def init_reg(message, session=None):

    """
    initiation registration of a user db doesn't have
    :param message: from decorator
    :param session: from decorator sessions_dec
    :return: reg func running on a separated thread
    """
    thread = threading.Thread(target=reg, args=(message,))
    thread.start()


def create_list_keyboard(list):

    """
    Creating simple reply keyboard markup with list elements
    :param list: list of elements
    :return: keyboard
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for el in list:
        keyboard.add(types.KeyboardButton(text=el))
    return keyboard



@session_dec
def reg(message, session=None):

    """
    Setting a user with current id by asking him either item to edit or data to add. Every attempt asking if state is set
    to one of empty attribute (if so set attr = state as message.text (cause if state is set then we're receiving
    data for attribute)) if not, then the state is either none or current attr is set already, so we have to set state
    equals name of next empty attribute.

    :param message: either user state or user attribute data
    :param session: session
    :return: end means either complete filling with user data or going to editing existing data
    """

    user = session.query(Users).filter(Users.id == message.chat.id).first()
    p = 'reg'
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)

    if user.state in states[p].keys():
        setattr(user, user.state, message.text)

    for k, v in states[p].items():
        if getattr(user, k) == None:
            user.state = k
            if user.state in reg_attr.keys():
                m1 = bot.send_message(message.chat.id, text=f'{v.title()}:',
                                 reply_markup=create_list_keyboard(reg_attr[k]))
                delete_after(m1, 0)
            else:
                m2 = bot.send_message(message.chat.id, text= f'{v.title()}:')
                delete_after(m2, 0)
            break

    if None not in [getattr(user, k) for k in states[p].keys()]:
        thread = threading.Thread(target=confirm_reg, args=(message, user))
        thread.start()
    else:
        bot.register_next_step_handler(message, reg)


def confirm_reg(message, user=None):

    """
    Sending message to confirm existing user data
    """

    p = 'reg'

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text='Подтвердить',
                                            callback_data=f'confirm_reg_data_mess{message.id}'),
                 types.InlineKeyboardButton(text='Редактировать',
                                            callback_data=f'edit_reg_data_mess{message.id}'))
    feedback = 'Ваши данные:\n\n' + \
               '\n'.join([f'{v.title()}: {getattr(user, k)}' for k, v in states[p].items()])
    feedback_data_message = bot.send_message(message.chat.id, text=feedback, reply_markup=keyboard)
    delete_after(feedback_data_message, 1)

@bot.callback_query_handler(func=lambda call: True if 'reg_data' in call.data else False)
@session_dec
def callback_confirm_reg(call, session=None):

    """
    Callback includes info about what user have chosen (confirm or edit)

    :param call: 'confirm_reg_data_mess' or 'confirm_reg_data_mess'
    """
    user = session.query(Users).filter(Users.id == call.message.chat.id).first()

    if 'confirm' in call.data:
        confirm_message = bot.send_message(call.message.chat.id, text='Подтверждено')
        delete_after(confirm_message, 0)
    elif 'edit' in call.data:
        user.state = 'edit'
        session.commit()
        thread = threading.Thread(target=edit_personal_reg_data, args=(call.message,))
        thread.start()


@session_dec
def edit_personal_reg_data(message, session=None):

    """
    Current iteration depends on user state and message. Bot shows user his info, asks what to edit then record it. Also
    requires confirmation.
    """
    user = session.query(Users).filter(Users.id == message.chat.id).first()
    p = 'reg'
    feedback = 'Выберите что надо исправить:\n\n' + \
               '\n'.join([f'/{k}: {getattr(user, k)}' for k, v in states[p].items()]) + \
               '\n\nДля завершения нажмите /end'

    try: bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    except: pass

    if message.text == '/end':
        user.state = None
        complete_message = bot.send_message(message.chat.id, text='Завершено')
        delete_after(complete_message, 1)
        delete_after(message, 1)
    elif user.state == 'edit':
        ask_user_reg_attr(feedback, user, message)
    elif message.text[1:] in states[p].keys():
        position = message.text[1:]
        get_reg_data(user, message, position)
    elif user.state in states[p].keys():
        set_reg_items(user, message)


def ask_user_reg_attr(feedback, user, message):

    'Secondary function in chain of getting state'

    user.state = None
    feedback_message = bot.send_message(message.chat.id, text=feedback)
    delete_after(feedback_message, 1)
    delete_after(message, 1)
    bot.register_next_step_handler(message, edit_personal_reg_data)


def get_reg_data(user, message, position):

    'Secondary function to get data from user'

    try: bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    except: pass

    if position in reg_attr.keys():
        choose_correct_data_message = bot.send_message(message.chat.id, text='Выберите корректные данные',
                         reply_markup=create_list_keyboard(reg_attr[message.text[1:]]))
        delete_after(choose_correct_data_message, 1)
    else:
        state_data_message = bot.send_message(message.chat.id, states['reg'][message.text[1:]].title() + ':')
        delete_after(state_data_message, 1)
    user.state = message.text[1:]
    bot.register_next_step_handler(message, edit_personal_reg_data)


def set_reg_items(user, message):

    'Secondary function to set data to DB also checking if its accurate'

    if (user.state in reg_attr.keys() and message.text not in reg_attr[user.state]) \
            or (user.state == 'phone' and not any(i.isdigit() for i in message.text)):
        incorrect_data_message = bot.send_message(message.chat.id, text=f'Некорректные данные:\n{user.state}\n\nПопробуйте снова.')
        delete_after(incorrect_data_message, 1)
        bot.register_next_step_handler(message, edit_personal_reg_data)
    else:
        setattr(user, user.state, message.text)
        user.state = 'edit'
        thread = threading.Thread(target=edit_personal_reg_data, args=(message,))
        thread.start()


#instructions block
@bot.message_handler(commands='instructions')
@session_dec
def instructions(message, session=None):
    user = session.query(Users).filter(Users.id == message.chat.id).first()
    user.state = os.path.join(os.path.expanduser('~'), os.getcwd(), 'instructions')
    session.commit() #fixed
    thread = threading.Thread(target=provide_instruction, args=(message,))
    thread.start()


@session_dec
def provide_instruction(message, session=None):

    # bug 1: sends hidden file type like '$струкция...' // solved:
    # ghost file was deleted the same way it was found - via glob.glob and os.listdir

    # bug 2: requires 2 attempt to send '/instructions' command (something with setting user.state as None) //solved:
    # thread was creating before commit().

    "User's state - contains current path to instructions. When user gets to what he needs (an instruction file)"\
    "program will return it"

    user = session.query(Users).filter(Users.id == message.chat.id).first()

    if message.text != '/instructions':
        user.state = os.path.join(os.path.expanduser('~'), user.state, message.text)

    if not any([os.path.isfile(os.path.join(os.path.expanduser("~"), user.state, i)) for i in os.listdir(user.state)]):
        buttons = os.listdir(user.state)
        bot.send_message(message.chat.id, text='С чем вам нужна помощь?', reply_markup=create_list_keyboard(buttons))
        bot.register_next_step_handler(message, provide_instruction)
    else:
        for i in os.listdir(user.state):
            doc = open(os.path.join(os.path.expanduser("~"), user.state, i), 'rb')
            bot.send_document(message.chat.id, doc)
        user.state = None


@bot.message_handler(commands='create_queue')
def send_it_already(message):
    queue = task_queue.create_test_queue()
    print('queue:', queue)
    queue.queue_task('test')
    task = queue.create_tes
    bot.send_message(chat_id=task.send_task()[0],
                     text=task.send_task()[1],
                     reply_markup=task.send_task()[2])

@bot.callback_query_handler(func = lambda call: True if 'task_complete' in call.data else False)
def send_task_to_next_user(call):
    print(f'im in task_complete: {call.data}')
    queue = task_queue.get_queue_of_task(call.data[14:])
    print(queue)
    mess_data = queue.send_task_next_user()
    bot.send_message(chat_id=mess_data[0],
                     text=mess_data[1],
                     reply_markup=mess_data[2])

@bot.message_handler(commands='view_tasks')
@session_dec
def view_tasks(message, session=None):
    try:
        required_tasks = session.query(tasks.Task).all()
    except Exception as err:
        print(err)
    print('tasks', required_tasks)
    message_text = ''
    for task in required_tasks:
        message_text += '\n'+task.id
    bot.send_message(message.chat.id, text=message_text)

#test commands
@bot.message_handler(commands='set_state_to_none')
@session_dec
def set_state_to_none(message, session = None):
    user = session.query(Users).filter(Users.id == message.chat.id).first()
    user.state = None

@bot.message_handler(commands='set_to_none')
def set_to_none(message):
    remove_user(message.chat.id)
    add_user(message.chat.id)


@bot.message_handler(commands='get_user_info')
@session_dec
def get_user_info(message, session=None):
    user = session.query(Users).filter(Users.id == message.chat.id).first()
    for key in states['reg']:
        print(getattr(user, key))


@session_dec
def check_if_in_users(session, id):
    if len(session.query(Users).filter(Users.id == id).all()) == 0:
        return False
    else:
        return True


@bot.message_handler(commands='get_state')
@session_dec
def get_state(message, session=None):
    bot.send_message(message.chat.id, str(session.query(Users).filter(Users.id == message.chat.id).first().state))


#experimantal
@bot.message_handler(commands='send_test')
def send_test_message(message):
    msg = bot.send_message(message.chat.id, text='this is a test message')
    delete_after(msg, 1)


if __name__ == '__main__':
    app.run()