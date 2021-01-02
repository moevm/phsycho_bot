import json
db = {}

def push_user_feeling(user, feeling, date):
    if user not in db:
        db[user] = { 'feelings': [] }
   
    db[user]['feelings'].append({'feel':feeling, 'date':date})


def get_user_feelings(user):
    
    return "Вы сообщали о своем состоянии " + str(len(db[user]['feelings'])) + " раз"

def get_user_list():
    return db.keys()
