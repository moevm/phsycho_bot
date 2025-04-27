import datetime
import logging
import sys
import time
from typing import List
from collections import Counter

import pytz
import schedule
from telegram.ext import Updater

from commands.handlers import (
    ask_ready,
    resume_survey,
    send_weekly_emotions_report
)

from databases.db import (
    get_schedule_list_for_feeling_ask,
    Schedule,
    get_users_not_finish_survey,
    get_users,
    get_user_emotions_statistics

)

MINUTES_FOR_LOOP = 1
DAYS_OFFSET = 7


def cron(updater):
    logger = logging.getLogger(__name__)
    today = datetime.datetime.utcnow().date()
    schedules: List[Schedule] = get_schedule_list_for_feeling_ask()
    filter_schedules: List[Schedule] = []
    for _schedule in schedules:
        available_schedule = True
        for send_item in _schedule.sending_list:
            if 'date' in send_item:
                if send_item['date'].date() == today and not _schedule.is_test:
                    available_schedule = False
                    break
        if not available_schedule:
            continue

        count_added = 0
        for focus in _schedule.user.focuses:
            focus_date = focus['date']
            today = datetime.datetime.now()
            if today <= focus_date + datetime.timedelta(days=DAYS_OFFSET):
                count_added += 1
                if count_added > 1:
                    continue
                filter_schedules.append(_schedule)
        if count_added > 1:
            logger.warning("Unexpected count of user's feelings")

    for _schedule in filter_schedules:
        if _schedule.is_test:
            _schedule.is_on = False
            _schedule.save()
        ask_ready(updater, _schedule)


def ask_resume_survey(updater):
    users = get_users_not_finish_survey()
    for user in users:
        if user['time_not_finish'] > datetime.timedelta(days=0, seconds=7200):
            resume_survey(updater, user['id'])


def weekly_emotions_statistics(updater):
    end_date = pytz.utc.localize(datetime.datetime.utcnow())
    start_date = end_date - datetime.timedelta(weeks=1)

    users = get_users()
    for user in users:
        emotions_statistics = get_user_emotions_statistics(user['id'], start_date, end_date)
        if not emotions_statistics:
            continue
        emotion_counter = Counter(emotions_statistics)

        send_weekly_emotions_report(updater, user['id'], emotion_counter)


def main(token):
    # init_logger()
    updater = Updater(token, use_context=True)
    schedule.every(MINUTES_FOR_LOOP).minutes.do(cron, updater=updater)
    schedule.every().hour.do(ask_resume_survey, updater=updater)
    schedule.every().sunday.at("20:00").do(weekly_emotions_statistics, updater=updater)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main(sys.argv[1])
