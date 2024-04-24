from datetime import datetime
from typing import Optional

from pymodm import fields, MongoModel
from bson.objectid import ObjectId
from bson.errors import InvalidId

from databases.db import User


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
    Question(
        user_id=user.id,
        username=user.username,
        text=text,
        answered=False,
        date=datetime.now(),
        select=-1
    ).save()


def get_question(quest_id: str) -> Optional[Question]:
    try:
        return Question.objects.get({'_id': ObjectId(quest_id)})
    except (InvalidId, Question.DoesNotExist):
        return None


def list_questions() -> list:
    queries = Question.objects.raw(
        {'answered': False}
    )
    return list(queries.aggregate({'$sort': {'date': -1}}))


def select_question(user_id, question) -> None:
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
    question_id = fields.CharField()
    user_id = fields.IntegerField()
    username = fields.CharField()
    text = fields.CharField()
    date = fields.DateTimeField()


def init_answer(question_id, text):
    if not text:
        return

    Answer(
        question_id=question_id,
        text=text,
        date=datetime.now()
    ).save()

    question = get_question(question_id)
    question.answered = True
    question.select = -1
    question.save()


def get_answer(quest_id) -> Optional[Answer]:
    try:
        return Answer.objects.get({'question_id': quest_id})
    except Answer.DoesNotExist:
        return None


def to_str_question(quest_dict: dict) -> str:
    return (f'_id: {quest_dict["_id"]} \nСпрашивает: {quest_dict["username"]} '
            f'\nВопрос: {quest_dict["text"]} \n{quest_dict["date"].strftime("%m/%d/%Y, %H:%M:%S")}')


def to_str_answer(answer) -> str:
    return f'Ответ: {answer.text} \n{answer.date.strftime("%m/%d/%Y, %H:%M:%S")}'
