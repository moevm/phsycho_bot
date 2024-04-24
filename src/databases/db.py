import datetime
import logging
from typing import List, Optional
from string import punctuation
from collections import Counter
import nltk
from nltk.corpus import stopwords
from pymystem3 import Mystem

import pytz
from pymodm import connect, fields, MongoModel
from pymodm.connection import _get_db
import gridfs


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
    DEBUG: get_datetime_with_tz(START_UNIX, datetime.datetime.utcnow().time()),
}


class User(MongoModel):
    id = fields.IntegerField()
    username = fields.CharField(blank=True)
    chosen_name = fields.CharField()
    first_name = fields.CharField()
    last_name = fields.CharField()
    is_admin = fields.BooleanField()
    is_bot = fields.BooleanField()
    language_code = fields.CharField()
    initial_reason = fields.CharField()
    initial_reason_flag = fields.BooleanField()  # True - ready to set initial_reason
    focuses = fields.ListField(fields.DictField())
    feelings = fields.ListField(fields.DictField())
    ready_flag = fields.BooleanField()
    last_usage = fields.DateTimeField()
    preferences = fields.ListField(fields.DictField())  # [{"voice mode": False - text mode}, {"pronoun": True - Вы}]

    def get_last_focus(self):
        if self.focuses and len(self.focuses) > 0:
            return self.focuses[-1]['focus']

        return 'f_no_focus'

    # def __str__(self):
    #     return f'{self.id} | {self.first_name} | {self.last_name}'

    def __str__(self):
        return f'{self.id} | {self.language_code} | {self.first_name} | {self.last_name}'


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
    audio_file = fields.FileField()
    time_send_question = fields.DateTimeField()
    time_receive_answer = fields.DateTimeField()
    stats = fields.CharField()

    def __str__(self):
        return (
            f'{self.user=} | '
            f'{self.survey_id=} | '
            f'{self.survey_step=} | '
            f'{self.survey_next=} | '
            f'{self.need_answer=} | '
            f'{self.user_answer=} | '
            f'{self.stats=} | '
            f'{self.audio_file=} | '
            f'{self.time_send_question=}, '
            f'{self.time_receive_answer=}'
        )


class Survey(MongoModel):
    id = fields.IntegerField()
    title = fields.CharField()
    count_of_questions = fields.IntegerField()

    def __str__(self):
        return f'{self.id} | {self.title} | {self.count_of_questions}'


class BotAudioAnswer(MongoModel):
    id = fields.IntegerField()
    audio_answer = fields.FileField()
    text_of_audio_answer = fields.CharField()
    time_send_answer = fields.DateTimeField()

    def __str__(self) -> str:
        return (
            f'{self.id=} | '
            f'{self.audio_answer=} | '
            f'{self.text_of_audio_answer=} | '
            f'{self.time_send_answer=}'
        )


def get_user(user_id: int) -> Optional[User]:
    try:
        return User.objects.get({'id': user_id})
    except User.DoesNotExist:
        return None


def create_admin(user_id: int) -> None:
    user = get_user(user_id)

    if user:
        if not user.is_admin:
            user.is_admin = True
            user.save()

    else:
        User(
            id=user_id,
            first_name='Admin',
            is_bot=False,
            is_admin=True,
            username='admin',
            language_code='ru',
        ).save()


def update_info(user) -> None:
    db_user = init_user(user)

    if not db_user:
        return

    db_user.last_name = user.last_name
    db_user.first_name = user.first_name
    db_user.username = user.username
    db_user.is_bot = user.is_bot
    db_user.save()


def init_user(user) -> User:
    try:
        return User.objects.get({'id': user.id})
    except User.DoesNotExist:
        return User(
            id=user.id,
            first_name=user.first_name,
            is_bot=user.is_bot,
            is_admin=False,
            username=user.username,
            chosen_name=' ',
            initial_reason=' ',
            initial_reason_flag=False,
            language_code=user.language_code,
        ).save()


def init_survey_progress(
        user,
        focus,
        id_=0,
        survey_step=0,
        next_step=1,
        need_answer=False,
        user_answer="INIT PROGRESS",
        stats="",
        audio_file=None,
) -> SurveyProgress:
    date = pytz.utc.localize(datetime.datetime.utcnow())
    return SurveyProgress(
        id=id_,
        user=user,
        survey_id=focus,
        survey_step=survey_step,
        survey_next=survey_step + 1,
        need_answer=need_answer,
        user_answer=user_answer,
        audio_file=audio_file,
        stats=stats,
        time_send_question=date,
        time_receive_answer=date,
    )


def get_user_answer(user, focus, step) -> str:
    list_survey_progress = SurveyProgress.objects.raw({'survey_id': focus})
    for survey_step in list_survey_progress.reverse():
        if survey_step.user.id == user.id and survey_step.survey_step == step:
            return survey_step.user_answer
    return ''


def get_user_word_statistics(user_id, start_date=None, end_date=None):
    nltk.download('stopwords')
    mystem = Mystem()

    if start_date and end_date:
        survey_progress_objects = SurveyProgress.objects.raw({
            'time_receive_answer': {
                '$gte': start_date,
                '$lt': end_date
            }
        })
    else:
        survey_progress_objects = SurveyProgress.objects.all()
    answers = ' '.join(map(lambda x: x.user_answer, filter(lambda x: x.user.id == user_id, survey_progress_objects)))

    tokens = mystem.lemmatize(answers.lower())
    stop_words = set(stopwords.words('russian'))
    tokens = list(filter(lambda token: token not in stop_words and token.strip() not in punctuation, tokens))

    return dict(Counter(tokens))


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
    schedules: List[Schedule] = list(
        Schedule.objects.raw(
            {
                # 'user': {'$elemMatch': {'id': user.id}},
                'is_test': is_test
            }
        )
    )
    filter_schedules = []
    for schedule in schedules:
        if schedule.user.id == user.id:
            filter_schedules.append(schedule)
    if len(filter_schedules) == 0:
        logger.error('len(filter_schedules) == 0')
    if len(filter_schedules) > 1:
        logger.warning('len(filter_schedules) > 1')
    return filter_schedules[0]


def push_user_chosen_name(user, name):
    db_user = init_user(user)
    db_user.chosen_name = name
    db_user.save()


def get_user_chosen_name(user):
    db_user = init_user(user)
    return db_user.chosen_name


def get_user_initial_reason(user):
    db_user = init_user(user)
    return db_user.initial_reason


def push_user_initial_reason(user, reason):
    db_user = init_user(user)
    db_user.initial_reason = reason
    db_user.save()


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


def push_user_survey_progress(
        user,
        focus,
        id_=0,
        survey_step=0,
        _=1,
        need_answer=False,
        user_answer="INIT PROGRESS",
        stats="",
        audio_file=None,
):
    date = pytz.utc.localize(datetime.datetime.utcnow())
    db_user = init_user(user)
    SurveyProgress(
        id=id_,
        user=db_user,
        survey_id=focus,
        survey_step=survey_step,
        survey_next=survey_step + 1,
        need_answer=need_answer,
        user_answer=user_answer,
        audio_file=audio_file,
        stats=stats,
        time_send_question=date,
        time_receive_answer=date,
    ).save()


def push_bot_answer(id_=0, answer=None, text=""):
    date = pytz.utc.localize(datetime.datetime.utcnow())
    BotAudioAnswer(
        id=id_, audio_answer=answer, text_of_audio_answer=text, time_send_answer=date
    ).save()


def get_user_feelings(user):
    db_user = init_user(user)
    return f"Вы сообщали о своем состоянии {len(list(db_user.feelings))} раз"


def push_user_mode(user, mode):
    db_user = init_user(user)
    for preference in db_user.preferences:
        if "voice mode" in preference:
            preference["voice mode"] = mode
            db_user.save()
            return
    db_user.preferences.append({"voice mode": mode})
    db_user.save()


def change_user_mode(user):
    db_user = init_user(user)
    for preference in db_user.preferences:
        if "voice mode" in preference:
            preference["voice mode"] = not preference["voice mode"]
            break
    else:
        db_user.preferences.append({"voice mode": True})
    db_user.save()


def get_user_mode(user):
    db_user = init_user(user)
    for preference in db_user.preferences:
        if "voice mode" in preference:
            return preference["voice mode"]
    return False


def change_user_pronoun(user):
    db_user = init_user(user)
    for preference in db_user.preferences:
        if "pronoun" in preference:
            preference["pronoun"] = not preference["pronoun"]
            break
    else:
        db_user.preferences.append({"pronoun": True})
    db_user.save()


def get_user_pronoun(user):
    db_user = init_user(user)
    for preference in db_user.preferences:
        if "pronoun" in preference:
            return preference["pronoun"]
    return False


def push_user_pronoun(user, pronoun):
    db_user = init_user(user)
    for preference in db_user.preferences:
        if "pronoun" in preference:
            preference["pronoun"] = pronoun
            db_user.save()
            return
    db_user.preferences.append({"pronoun": pronoun})
    db_user.save()


def get_user_audio(user):
    progress = list(SurveyProgress.objects.values().all())
    file_storage = gridfs.GridFSBucket(_get_db())
    audio_file = file_storage.open_download_stream(progress[-1]["audio_file"])._id
    # print(audio_file)
    # audio_id = file_storage.find({"filename": 'audio_file'}, no_cursor_timeout=True).distinct('_id')
    # print(json.loads(json_util.dumps(audio_id)))
    return audio_file


def get_bot_audio():
    answer = list(BotAudioAnswer.objects.values().all())
    file_storage = gridfs.GridFSBucket(_get_db())
    bot_audio = file_storage.open_download_stream(answer[-1]["audio_answer"]).read()
    return bot_audio


def set_user_ready_flag(user, flag):
    db_user = init_user(user)
    db_user.ready_flag = flag
    db_user.save()


def set_user_initial_reason_flag(user, flag):
    db_user = init_user(user)
    db_user.initial_reason_flag = flag
    db_user.save()


def get_user_initial_reason_flag(user):
    db_user = init_user(user)
    return db_user.initial_reason_flag


def set_schedule_is_on_flag(schedule, flag):
    schedule.is_on = flag
    schedule.save()


def set_schedule_asked_today(schedule):
    schedule.sending_list.append(
        {'date': pytz.utc.localize(datetime.datetime.utcnow()), 'success': True}
    )
    schedule.save()


def get_schedule_list_for_feeling_ask():
    now = datetime.datetime.utcnow().time()
    # TODO: think about time
    today = datetime.datetime(year=1970, month=1, day=1)
    dt_from = get_datetime_with_tz(today, datetime.time(hour=now.hour))
    dt_to = get_datetime_with_tz(today, datetime.time(hour=now.hour)) + datetime.timedelta(hours=1)
    return list(
        Schedule.objects.raw({'time_to_ask': {'$gte': dt_from, '$lt': dt_to}, 'is_on': True})
    )


def get_users_not_finish_survey():
    users = []
    for user in User.objects.raw({'focuses': {'$exists': True}}):
        last_focus = user.get_last_focus()
        survey_progress = get_survey_progress(user, last_focus)
        if survey_progress.need_answer:
            list_survey_progress = SurveyProgress.objects.raw({'survey_id': last_focus})
            for i in list_survey_progress:
                if i.user.id == user.id and i.survey_step == 0:
                    start_time = i.time_send_question
                    time_not_finish = datetime.datetime.utcnow() - start_time
            users.append(
                {
                    'id': user.id,
                    'username': user.username,
                    'survey_type': last_focus,
                    'start_time': start_time,
                    'time_not_finish': time_not_finish,
                    'survey_step': survey_progress.survey_step,
                }
            )
    return users


def set_last_usage(user):
    db_user = init_user(user)
    db_user.last_usage = pytz.utc.localize(datetime.datetime.utcnow())
    db_user.save()


def get_users_not_answer_last24hours():
    users = []
    for user in User.objects.all():
        if user.last_usage is None or pytz.utc.localize(user.last_usage) < pytz.utc.localize(
                datetime.datetime.utcnow()
        ) - datetime.timedelta(days=1):
            users.append({'id': user.id, 'username': user.username})
    return users


def auth_in_db(username, password):
    connect(f'mongodb://{username}:{password}@db:27017/{DATABASE_NAME}?authSource=admin')
