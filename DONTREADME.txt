1. Regestration bloc.

Records new empty user given access level 1 as default (later need to figure out how to user it).

1.1 def reg 
	works as a cycle running each iteration through user data untill finds a None equaling attribute. 
When it hits it, it sets user.state = attribute name and breaks the cycle. Also apart from == None if cehcks if 
user.state was in the list of attributes. 
Before checking for None in attr it checks if user.state is equals one of the attributes name.

At last it checks if there's no more Nones so it can go to confirmation function.

1.2. def edit_personal_reg_data
	basicly works the same way but gives user to choose what he wants to edit by sending him user data in a 
message with attribut names marked with "/" and its values. The "/" is used for user so it highlights in dialog 
window in Telegram to quick press & send.

Cycling algorythm works in simiilar way with def reg

2. Providing user with instructions by hitting '/instructions' command is done in 2 functions. The major problem in telebot
1.0 was that each file required its own command. Here bot asks user what he needs to help with which is actually name 
of directory with instructions (with increasing number of folders and instructions the "go back" button will be nessesary).

3. Task block.

sqlalchemy class Tasks:

each task contains:
	-id;
	-user_in_line// index in users_in_line of a current user who works on task
	-users_in_line; // (list) users who will work on task by their order in list
	-creation_date; // the only and unchangeble date of task record
	-updating_date; // the date when the task was set on the current slave_id user
	-duration; // amount of days requiered to solve task on every stage
	-deadline; // the date of deadline of current slave
	-title; // description of what every slave needs to do (the title will be one equal for everyone so it'll be the threshold not to 		make lots of slaves
	-attachments; // string with links to folders with attachments (docs, images, txt messages etc)
	-state; // string describing current status of task ([processing, complete])
	-parent_id; // id of a parent tast or regular task	

def switch_to_next_slave(user_in_line, uesrs_in_line):
	"""user_in_line + 1"""
	pass

def get_slave_id(user_in_line, users_in_line):
	return user_in_line[user_in_line]

""" it easier to use SBIS API"""
UPD: this format has to be remade.
	class task hasa to be link only to CURRENT user. When he completes it, it just returns status 'complete'.
	
	If I want to createa a queue of tasks, I have to create another class 'Queue' to store there info about this process (turns, user ids, deadline or whole process(?), 
""""""

