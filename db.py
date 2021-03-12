import datetime

from pymodm import connect, fields, MongoModel


def get_seconds(t: datetime.time) -> int:
    return (t.hour * 60 + t.minute) * 60 + t.second


DEBUG = 's_right_now'
DATABASE_NAME = 'phsycho_bot'
COLLECTION_NAME = 'dataset'
TIME_VALUES = {
    # TODO: ---------------
    's_18': 18 * 60 * 60,
    's_19': 19 * 60 * 60,
    's_20': 20 * 60 * 60,
    # TODO: ---------------
    DEBUG: get_seconds(datetime.datetime.now().time())
}

connect(f'mongodb://localhost:27017/{DATABASE_NAME}')


class User(MongoModel):
    id = fields.IntegerField()
    username = fields.CharField()
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
        return f'[id] - {self.id} | [user] - {self.user} | [survey_step] - {self.survey_step} ' \
               f'| [done] - {self.done} | [time_to_send] - {self.time_to_send}'


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


def push_user_schedule(user, schedule, date):
    # sending every day
    # TODO: param date is unused
    is_test = False
    if schedule == DEBUG:
        is_test = True
    db_user = init_user(user)
    Schedule(**{
        'user': db_user,
        'time_to_ask': TIME_VALUES[schedule],
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


def get_schedule_list_for_feeling_ask():
    now = datetime.datetime.now().time()
    # TODO: think about time
    today = datetime.datetime.now().date().today()
    today = datetime.datetime(year=1970, month=1, day=1)
    dt_from = datetime.datetime.combine(today, datetime.time(hour=now.hour))
    dt_to = datetime.datetime.combine(today, datetime.time(hour=now.hour + 1))
    print(dt_from)
    print(dt_to)
    return list(Schedule.objects.raw({
        'time_to_ask': {
            '$gte': dt_from,
            '$lt': dt_to,
        },
        'is_on': True
    }))
