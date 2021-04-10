import datetime
import logging
from typing import List

import pytz
from pymodm import connect, fields, MongoModel

START_UNIX = datetime.datetime(year=1970, month=1, day=1)
DEBUG = 's_right_now'
DATABASE_NAME = 'phsycho_bot'
COLLECTION_NAME = 'dataset'

TIME_VALUES = {}


def get_datetime_with_tz(date: datetime.date, time: datetime.time):
    return pytz.utc.localize(datetime.datetime.combine(date, time))


def get_datetime_via_hour_msk(hour: int):
    return get_datetime_with_tz(START_UNIX, datetime.time(hour=(hour - 3) % 24))


def get_datetime_via_hour_utc(hour: int):
    return get_datetime_with_tz(START_UNIX, datetime.time(hour=hour % 24))


def get_datetime_via_time(time: datetime.time):
    return get_datetime_with_tz(START_UNIX, time)


def init_time_values():
    for i in range(24):
        TIME_VALUES[f's_{i}'] = {
            'time': get_datetime_via_hour_msk(i),
            'caption': '{hour_start:0>2}:00 - {hour_end:0>2}:00'.format(hour_start=i, hour_end=i + 1)
        }
    TIME_VALUES['s_right_now'] = {
        'time': get_datetime_via_time(datetime.datetime.utcnow().time()),
        'caption': 'Прямо чейчас'
    }


init_time_values()


class User(MongoModel):
    id = fields.IntegerField()
    username = fields.CharField(blank=True)
    first_name = fields.CharField()
    last_name = fields.CharField()
    is_bot = fields.BooleanField()
    language_code = fields.CharField()
    focuses = fields.ListField(fields.DictField())
    feelings = fields.ListField(fields.DictField())
    ready_flag = fields.BooleanField()

    def __str__(self):
        return f'[id] - {self.id} | [first_name] - {self.first_name} | [last_name] - {self.last_name}'


class Schedule(MongoModel):
    # id = fields.IntegerField()
    user = fields.ReferenceField(User)
    # survey_step = fields.IntegerField()
    time_to_ask = fields.DateTimeField()
    """
    sending_list = [
        {'date': '2021-03-02', 'success': True},
        {'date': '2021-03-03', 'success': False},
        {'date': '2021-03-04', 'success': True},
        {'date': '2021-03-05', 'success': True},
    ]
    """
    sending_list = fields.ListField(fields.DictField())
    is_test = fields.BooleanField()
    is_on = fields.BooleanField()

    def __str__(self):
        return f'Schedule is {self.is_on}'


class SurveyProgress(MongoModel):
    id = fields.IntegerField()
    user = fields.ReferenceField(User)
    survey_id = fields.IntegerField()
    survey_step = fields.IntegerField()
    user_answer = fields.CharField()

    time_send_question = fields.DateTimeField()
    time_receive_answer = fields.DateTimeField()

    def __str__(self):
        return f'[id] - {self.id} | [user] -  {self.user} | [survey_id] - {self.survey_id} | ' \
               f'[survey_step] - {self.survey_step} | [user_answer] - {self.user_answer} | ' \
               f'[time_send_question] - {self.time_send_question} | [time_receive_answer] - {self.time_receive_answer}'


class Survey(MongoModel):
    id = fields.IntegerField()
    title = fields.CharField()
    count_of_questions = fields.IntegerField()

    def __str__(self):
        return f'[id] - {self.id} | [title] -  {self.title} | [count_of_questions] - {self.count_of_questions}'


def init_user(user) -> User:
    try:
        return User.objects.get({'id': user.id})
    except User.DoesNotExist:
        return User(**{
            'id': user.id,
            'first_name': user.first_name,
            'is_bot': user.is_bot,
            'username': user.username,
            'language_code': user.language_code
        }).save()


def get_schedule_by_user(user, is_test=True):
    logger = logging.getLogger(__name__)
    schedules: List[Schedule] = list(Schedule.objects.raw({
        'is_test': is_test
    }))
    filter_schedules = []
    for schedule in schedules:
        if schedule.user.id == user.id:
            filter_schedules.append(schedule)
    if len(filter_schedules) == 0:
        logger.error('len(filter_schedules) == 0')
    if len(filter_schedules) > 1:
        logger.warning('len(filter_schedules) > 1')
    return filter_schedules[0]


def push_user_schedule(user, schedule, date):
    # sending every day
    # TODO: param date is unused
    is_test = False
    if schedule == DEBUG:
        is_test = True
    db_user = init_user(user)
    Schedule(**{
        'user': db_user,
        'time_to_ask': TIME_VALUES[schedule]['time'],
        'is_test': is_test,
        'is_on': True
    }).save()


def push_user_focus(user, focus, date):
    db_user = init_user(user)
    db_user.focuses.append({'focus': focus, 'date': date})
    db_user.save()


def push_user_feeling(user, feeling, date):
    db_user = init_user(user)
    db_user.feelings.append({'feel': feeling, 'date': date})
    db_user.save()


def get_user_feelings(user):
    db_user = init_user(user)
    return f"Вы сообщали о своем состоянии {len(list(db_user.feelings))} раз"


def set_user_ready_flag(user, flag):
    db_user = init_user(user)
    db_user.ready_flag = flag
    db_user.save()


def set_schedule_is_on_flag(schedule, flag):
    schedule.is_on = flag
    schedule.save()


def set_schedule_asked_today(schedule):
    schedule.sending_list.append({'date': pytz.utc.localize(datetime.datetime.utcnow()), 'success': True})
    schedule.save()


def get_schedule_list_for_feeling_ask():
    now = datetime.datetime.utcnow().time()
    # TODO: think about time
    dt_from = get_datetime_via_hour_utc(now.hour)
    dt_to = get_datetime_via_hour_utc(now.hour + 1)
    return list(Schedule.objects.raw({
        'time_to_ask': {
            '$gte': dt_from,
            '$lt': dt_to,
        },
        'is_on': True
    }))


def auth_in_db(username, password):
    connect(f'mongodb://{username}:{password}@db:27017/{DATABASE_NAME}?authSource=admin')
