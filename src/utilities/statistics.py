import datetime
from typing import Optional

from databases import db


class Statistics:
    def __init__(self):
        self.period = 'day'

    def set_period(self, period: str) -> None:
        if period in ('day', 'week', 'month', 'year'):
            self.period = period

    def get_period(
            self, start_day: datetime.date = None, period: str = None
    ) -> Optional[tuple[datetime.date, datetime.date]]:
        today = start_day
        if start_day is None:
            today = datetime.date.today()

        period_value = period
        if period is None:
            period_value = self.period

        match period_value:
            case 'day':
                timedelta = datetime.timedelta(days=1)
                end_day = today + timedelta
            case 'week':
                timedelta = datetime.timedelta(weeks=1)
                end_day = today + timedelta
            case 'month':
                timedelta = datetime.timedelta(days=30)
                end_day = today + timedelta
            case 'year':
                timedelta = datetime.timedelta(days=365)
                end_day = today + timedelta
            case _:
                print(f"Warning: unknown period '{self.period}'")
                return None
        return today, end_day

    @staticmethod
    def get_new_users_for_period(
            start_date: datetime.date, end_date: datetime.date
    ) -> tuple[list, int]:
        """
        :return: list of questions like list[dict], not list[User]
        """

        start, end = start_date, end_date
        if not isinstance(start_date, datetime.date) or not isinstance(end_date, datetime.date):
            raise TypeError(f"Error: wrong type of date, expected datetime.date")

        queries = db.User.objects.raw(
            {
                'registration_date': {
                    '$lt': end,
                    '$gte': start
                }
            },
            {
                'id': True
            }
        )

        count = queries.count()
        return list(queries), count

    @staticmethod
    def get_all_users_count() -> int:
        return db.User.objects.count()
