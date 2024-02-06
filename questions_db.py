from datetime import datetime
from typing import Optional

from pymodm import connect, fields, MongoModel, ObjectId
from bson.objectid import ObjectId

from db import User


class Question(MongoModel):
    user_id = fields.IntegerField()
    username = fields.CharField()
    text = fields.CharField()
    answered = fields.BooleanField()
    date = fields.DateTimeField()
    select = fields.IntegerField()

    def get_id(self):
        return self._id


def init_question(user: User, text):
    if text:
        Question(
            user_id=user.id,
            username=user.username,
            text=text,
            answered=False,
            date=datetime.now(),
            select=-1
        ).save()


def get_question(quest_id) -> Optional[Question]:
    try:
        return Question.objects.get({'_id': ObjectId(quest_id)})
    except Question.DoesNotExist:
        return None


def list_questions() -> list:
    queries = Question.objects.raw(
        {'answered': False}
    )
    return list(queries.aggregate({'$sort': {'date': -1}}))


def select_question(user_id) -> None:
    question = get_question(user_id)
    if question:
        question.select = user_id
        question.save()


def unselect_question(user_id) -> None:
    question = get_question(user_id)
    if question:
        question.select = -1
        question.save()


def get_selected(user_id) -> Optional[Question]:
    try:
        return Question.objects.get({'select': user_id})
    except Question.DoesNotExist:
        return None


class Answer(MongoModel):
    user_id = fields.IntegerField()
    username = fields.CharField()
    text = fields.CharField()
    date = fields.DateTimeField()


def init_answer(question_id, text):
    if text:
        Answer(
            id=question_id,
            text=text,
            date=datetime.now()
        ).save()

        question = get_question(question_id)
        question.answered = True
        question.select = -1
        question.save()


def get_answer(quest_id) -> Optional[Answer]:
    try:
        return Answer.objects.get({'id': quest_id})
    except Answer.DoesNotExist:
        return None


def dict_to_str_question(quest_dict: dict) -> str:
    return (f'question_id: {quest_dict["_id"]} \nusername: {quest_dict["username"]} '
            f'\nquestion: {quest_dict["text"]} \n{quest_dict["date"].strftime("%m/%d/%Y, %H:%M:%S")}')


def dict_to_str_answer(answer_dict: dict) -> str:
    return f'question: {answer_dict["text"]} \n{answer_dict["date"].strftime("%m/%d/%Y, %H:%M:%S")}'
