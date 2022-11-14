from datetime import datetime
from calendar import monthrange


class timerange:

    THIS_MONTH = 'this month'
    TODAY = 'today'

    def __init__(self, time_from=None, time_to=None):
        self.time_from = time_from
        self.time_to = time_to

    @classmethod
    def from_str(cls, text: str):
        if text == 'this month':
            carrytime = datetime.today()
            month_range = monthrange(carrytime.year, carrytime.month)
            return cls(
                datetime(carrytime.year, carrytime.month, 1, 0, 0, 0),
                datetime(carrytime.year, carrytime.month, month_range[1], 23, 59, 59)
            )
        if text == 'today':
            carrytime = datetime.today()
            return cls(
                datetime(carrytime.year, carrytime.month, carrytime.day, 0, 0, 0),
                datetime(carrytime.year, carrytime.month, carrytime.day, 23, 59, 59)
            )

        for f in [
            "%b-%Y",  # Oct-2022
            "%Y-%b",  # 2022-Oct
            "%m-%Y",  # 10-2022
            "%Y-%m",  # 2022-10
        ]:
            try:
                date = datetime.strptime(text, f)
                month_range = monthrange(date.year, date.month)
                return cls(
                    datetime(date.year, date.month, 1, 0, 0, 0),
                    datetime(date.year, date.month, month_range[1], 23, 59, 59)
                )
                break
            except Exception:
                continue
        return cls()

    def is_valid(self):
        return self.time_from is not None and self.time_to is not None


def is_number(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True
