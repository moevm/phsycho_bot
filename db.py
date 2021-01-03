import json
db = {}

def init_user(user):
    if user not in db:
        db[user] = { 'feelings': [] , 'focuses':[]}

def push_user_schedule(user, schedule, date):
    init_user(user)

    db[user]['schedule'] = schedule


def push_user_focus(user, focus, date):
    init_user(user)

    db[user]['focuses'].append({'focus':focus, 'date':date})
   
def push_user_feeling(user, feeling, date):
    init_user(user)

    db[user]['feelings'].append({'feel':feeling, 'date':date})

def get_user_feelings(user):
    
    return "Вы сообщали о своем состоянии " + str(len(db[user]['feelings'])) + " раз"


def set_user_ready_flag(user, flag):
    init_user(user)

    db[user]['ready'] = flag

def get_user_list_for_feeling_ask():
    result = []
    for user in db:
        if db[user].get('ready', False):
            result.append(user)
    return result
