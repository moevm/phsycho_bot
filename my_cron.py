import datetime
import logging
import sys
import time
from typing import List

import schedule
from telegram.ext import Updater

from bot import ask_ready
from db import get_schedule_list_for_feeling_ask, Schedule

MINUTES_FOR_LOOP = 1
DAYS_OFFSET = 7


def cron(updater):
    logger = logging.getLogger(__name__)
    logger.debug('Searching suitable schedules')
    today = datetime.datetime.utcnow().date()
    schedules: List[Schedule] = get_schedule_list_for_feeling_ask()
    filter_schedules: List[Schedule] = []
    logger.debug(f'Count of schedules: {len(schedules)}')
    for _schedule in schedules:
        available_schedule = True
        for send_item in _schedule.sending_list:
            if 'date' in send_item:
                if send_item['date'].date() == today and not _schedule.is_test:
                    available_schedule = False
                    logger.debug('This schedule has already sent today')
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

    logger.debug(f'Count of filter schedules: {len(filter_schedules)}')
    for _schedule in filter_schedules:
        if _schedule.is_test:
            _schedule.is_on = False
            _schedule.save()
        ask_ready(updater, _schedule)


def main(token):
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    updater = Updater(token, use_context=True)
    # TODO return back
    schedule.every(MINUTES_FOR_LOOP).seconds.do(cron, updater=updater)
    while True:
        schedule.run_pending()
        time.sleep(6)


if __name__ == '__main__':
    main(sys.argv[1])
