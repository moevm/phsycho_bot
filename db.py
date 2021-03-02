from pymodm import connect, fields, MongoModel

DATABASE_NAME = 'phsycho_bot'
COLLECTION_NAME = 'dataset'
TIME_VALUES = {
    's_18': 18 * 60 * 60,
    's_19': 19 * 60 * 60,
    's_20': 20 * 60 * 60,
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
    time_to_send = fields.IntegerField()  # using unix time
    """
    sending_list = [
        {'date': '2021-03-02', 'success': True},
        {'date': '2021-03-03', 'success': False},
        {'date': '2021-03-04', 'success': True},
        {'date': '2021-03-05', 'success': True},
    ]
    """
    sending_list = fields.ListField(fields.DictField())

    def __str__(self):
        return f'[id] - {self.id} | [user] - {self.user} | [survey_step] - {self.survey_step} ' \
               f'| [done] - {self.done} | [time_to_send] - {self.time_to_send}'


class SurveyProgress(MongoModel):
    id = fields.IntegerField()
    user = fields.ReferenceField(User)
    survey_id = fields.IntegerField()
    survey_step = fields.IntegerField()
    user_answer = fields.CharField()

    # using unix time
    time_send_question = fields.IntegerField()
    time_receive_answer = fields.IntegerField(default=-1, )

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
        d = eval(str(user))
        return User(**d).save()


def push_user_schedule(user, schedule, date):
    # sending every day
    # TODO: param date is unused
    db_user = init_user(user)
    Schedule(**{
        'user': db_user,
        'time_to_send': TIME_VALUES[schedule]
    }).save()


def push_user_focus(user, focus, date):
    db_user = init_user(user)
    db_user.feelings.append({'focus': focus, 'date': date})
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


def get_user_list_for_feeling_ask():
    return list(User.objects.filter({'ready_flag': True}))
