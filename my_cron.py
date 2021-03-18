import datetime
import logging
import time

import schedule
from telegram.ext import Updater

from bot import ask_ready
from db import get_schedule_list_for_feeling_ask


MINUTES_FOR_LOOP = 1


def cron(updater):
    schedules = get_schedule_list_for_feeling_ask()
    print(schedules)
    filter_schedules = []
    for _schedule in schedules:
        for focus in _schedule.user.focuses:
            focus_date = focus['date']
            today = datetime.datetime.now()
            if today <= focus_date + datetime.timedelta(days=7):
                filter_schedules.append(_schedule)

    for _schedule in filter_schedules:
        ask_ready(updater, _schedule)


def main(token):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    updater = Updater(token, use_context=True)
    schedule.every(MINUTES_FOR_LOOP).minutes.do(cron, updater=updater)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main('1126020892:AAEeIA88MF1vJ4SHxwgTOOFoyTU2YGuUTMs')
