from datetime import datetime
import logging
from typing import List, Union

import pytz
from pymodm import fields, MongoModel

from db import User, get_datetime_with_tz


class Question(MongoModel):
    user_id = fields.IntegerField()
    username = fields.CharField()
    text = fields.CharField()
    answered = fields.BooleanField()
    # answer = fields.ReferenceField(Answer)
    date = fields.DateTimeField()

    def __str__(self):
        return (f'{self._id} | {self.user_id} | {self.username} '
                f'\n {self.text} \n {self.date.strftime("%m/%d/%Y, %H:%M:%S")}')

    def get_id(self):
        return self._id


def init_question(user: User, text):
    if text:
        Question(
            user_id=user.id,
            username=user.username,
            text=text,
            answered=False,
            date=datetime.now()
        )


def get_question(quest_id) -> Union[Question, None]:
    try:
        return Question.objects.get({'_id': quest_id})
    except Question.DoesNotExist:
        return None


def list_questions() -> Union[list[Question], None]:
    try:
        return Question.objects.get({'answered': False})
    except Question.DoesNotExist:
        return None


class Answer(MongoModel):
    user_id = fields.IntegerField()
    username = fields.CharField()
    text = fields.CharField()
    date = fields.DateTimeField()

    def __str__(self):
        return f'{self.id} | {self.user_id} | {self.username} \n {self.text} \n {self.date}'


def init_answer(user: User, question: Question, text):
    if text:
        Answer(
            _id=question.get_id(),
            user_id=user.id,
            username=user.username,
            text=text,
            date=datetime.now()
        )

