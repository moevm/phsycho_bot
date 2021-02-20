import json
import pymongo

DATABASE_NAME = 'phsycho_bot'
COLLECTION_NAME = 'dataset'


class DataBase:
    def __init__(self):
        self.__client = pymongo.MongoClient('localhost', 27017)
        self.__db = self.__client[DATABASE_NAME]

        self.__collection = self.__db[COLLECTION_NAME]

    def get_collection(self):
        return self.__collection

    def insert(self, doc_or_docs):
        if isinstance(doc_or_docs, dict):
            return self.__collection.insert_one(doc_or_docs).inserted_id
        return self.__collection.insert_many(doc_or_docs).inserted_ids

    def find(self, filter_dict=None):
        return list(self.__collection.find(filter_dict))

    def remove(self, filter_dict=None):
        return self.__collection.delete_many(filter_dict).deleted_count

    def update(self, query_elements=None, update=None):
        return self.__collection.update_many(query_elements, update).modified_count


db = DataBase()

def init_user(user):
    if len(db.find({'user': user})) == 0:
        db.insert({'user': user, 'feelings': [] , 'focuses': []})


def push_user_schedule(user, schedule, date):
    # TODO: param date is unused
    init_user(user)
    db.update({'user': user}, {'$push': {'schedule': schedule}})


def push_user_focus(user, focus, date):
    init_user(user)
    db.update({'user': user}, {'$push': {'focuses': {'focus': focus, 'date': date}}})


def push_user_feeling(user, feeling, date):
    init_user(user)
    db.update({'user': user}, {'$push': {'feelings': {'feel': feeling, 'date': date}}})


def get_user_feelings(user):
    return f"Вы сообщали о своем состоянии {len(db[user]['feelings'])} раз"


def set_user_ready_flag(user, flag):
    init_user(user)
    db.update({'user': user}, {'$set': {'ready': flag}})


def get_user_list_for_feeling_ask():
    result = []
    dataset = db.find({'ready': False})
    for user_data in dataset:
        result.append(user_data['user'])
    return result
