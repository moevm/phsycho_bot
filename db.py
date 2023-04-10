import datetime
import logging
from typing import List

import pytz
from pymodm import connect, fields, MongoModel


def get_datetime_with_tz(date: datetime.date, time: datetime.time):
    return pytz.utc.localize(datetime.datetime.combine(date, time))


START_UNIX = datetime.datetime(year=1970, month=1, day=1)
DEBUG = 's_right_now'
DATABASE_NAME = 'phsycho_bot'
COLLECTION_NAME = 'dataset'
TIME_VALUES = {
    # TODO: ---------------
    's_18': get_datetime_with_tz(START_UNIX, datetime.time(hour=18 - 3)),
    's_19': get_datetime_with_tz(START_UNIX, datetime.time(hour=19 - 3)),
    's_20': get_datetime_with_tz(START_UNIX, datetime.time(hour=20 - 3)),
    's_21': get_datetime_with_tz(START_UNIX, datetime.time(hour=21 - 3)),
    's_22': get_datetime_with_tz(START_UNIX, datetime.time(hour=22 - 3)),
    's_23': get_datetime_with_tz(START_UNIX, datetime.time(hour=23 - 3)),
    # TODO: ---------------
    DEBUG: get_datetime_with_tz(START_UNIX, datetime.datetime.utcnow().time())
}


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
    last_usage = fields.DateTimeField()

    def __str__(self):
        return f'{self.id} | {self.first_name} | {self.last_name}'


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
    # survey_id = fields.IntegerField()
    survey_id = fields.CharField()
    survey_step = fields.IntegerField()
    survey_next = fields.IntegerField()
    need_answer = fields.BooleanField()
    user_answer = fields.CharField()
    is_voice = fields.BooleanField()
    time_send_question = fields.DateTimeField()
    time_receive_answer = fields.DateTimeField()
    stats = fields.CharField()


    def __str__(self):
        return f'{self.user} | {self.survey_id} | {self.survey_step} | {self.survey_next} | {self.need_answer} | {self.user_answer} | {self.stats} | {self.is_voice} | {self.time_send_question}, {self.time_receive_answer}'


class Survey(MongoModel):
    id = fields.IntegerField()
    title = fields.CharField()
    count_of_questions = fields.IntegerField()

    def __str__(self):
        return f'{self.id} | {self.title} | {self.count_of_questions}'


def init_user(user) -> User:
    try:
        return User.objects.get({'id': user.id})
    except User.DoesNotExist:
        return User(id=user.id, first_name=user.first_name, is_bot=user.is_bot, username=user.username, language_code=user.language_code).save()


def init_survey_progress(user, focus, id=0, survey_step=0, next_step=1, need_answer=False, user_answer="INIT PROGRESS", stats="", is_voice = False) -> SurveyProgress:
    date = pytz.utc.localize(datetime.datetime.utcnow())
    return SurveyProgress(id=id, user=user, survey_id=focus, survey_step=survey_step, survey_next=survey_step + 1, need_answer=need_answer, user_answer=user_answer, is_voice=is_voice, stats=stats, time_send_question=date, time_receive_answer=date)


def get_user_answer(user, focus, step) -> str:
    list_survey_progress = SurveyProgress.objects.raw({'survey_id': focus})
    for survey_step in list_survey_progress.reverse():
        if survey_step.user.id == user.id and survey_step.survey_step == step:
            return survey_step.user_answer


def get_survey_progress(user, focus) -> SurveyProgress:
    list_survey_progress = SurveyProgress.objects.raw({'survey_id': focus})
    filtered_survey = []
    for i in list_survey_progress:
        if i.user.id == user.id:
            filtered_survey.append(i)
    if len(filtered_survey) == 0:
        return init_survey_progress(user, focus)
    return filtered_survey[-1]


def get_schedule_by_user(user, is_test=True):
    logger = logging.getLogger(__name__)
    schedules: List[Schedule] = list(Schedule.objects.raw({
        # 'user': {'$elemMatch': {'id': user.id}},
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
    Schedule(user=db_user, time_to_ask=TIME_VALUES[schedule], is_test=is_test, is_on=True).save()


def push_user_focus(user, focus, date):
    db_user = init_user(user)
    db_user.focuses.append({'focus': focus, 'date': date})
    db_user.save()


def push_user_feeling(user, feeling, date):
    db_user = init_user(user)
    db_user.feelings.append({'feel': feeling, 'date': date})
    db_user.save()

def push_user_survey_progress(user, focus, id=0, survey_step=0, next_step=1, need_answer=False, user_answer="INIT PROGRESS", stats="", is_voice = False):
    date = pytz.utc.localize(datetime.datetime.utcnow())
    db_user = init_user(user)
    SurveyProgress(id=id, user=db_user, survey_id=focus, survey_step=survey_step, survey_next=survey_step + 1, need_answer=need_answer, user_answer=user_answer, is_voice=is_voice, stats=stats, time_send_question=date, time_receive_answer=date).save()
    

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
    today = datetime.datetime(year=1970, month=1, day=1)
    dt_from = get_datetime_with_tz(today, datetime.time(hour=now.hour))
    dt_to = get_datetime_with_tz(today, datetime.time(hour=now.hour)) + datetime.timedelta(hours=1)
    return list(Schedule.objects.raw({
        'time_to_ask': {
            '$gte': dt_from,
            '$lt': dt_to,
        },
        'is_on': True
    }))


def get_users_not_finish_survey():
    users = []
    for user in User.objects.raw({'focuses': {'$exists': True}}):
        last_focus = user.focuses[-1]['focus']
        survey_progress = get_survey_progress(user, last_focus)
        if survey_progress.need_answer:
            list_survey_progress = SurveyProgress.objects.raw({'survey_id': last_focus})
            for i in list_survey_progress:
                if i.user.id == user.id and i.survey_step == 0:
                    start_time = i.time_send_question
                    time_not_finish = datetime.datetime.utcnow() - start_time
            users.append({
                'id': user.id,
                'username': user.username,
                'survey_type': last_focus,
                'start_time': start_time,
                'time_not_finish': time_not_finish,
                'survey_step': survey_progress.survey_step,
            })
    return users


def set_last_usage(user):
    db_user = init_user(user)
    db_user.last_usage = pytz.utc.localize(datetime.datetime.utcnow())
    db_user.save()


def get_users_not_answer_last24hours():
    users = []
    for user in User.objects.all():
        if user.last_usage==None or pytz.utc.localize(user.last_usage) < pytz.utc.localize(datetime.datetime.utcnow()) - datetime.timedelta(days=1):
            users.append({
                'id': user.id,
                'username': user.username
            })
    return users


def auth_in_db(username, password):
    connect(f'mongodb://{username}:{password}@db:27017/{DATABASE_NAME}?authSource=admin')
