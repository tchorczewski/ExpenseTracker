from datetime import datetime

from dateutil.relativedelta import relativedelta


def get_previous_month() -> tuple:
    current_date = datetime.now()
    previous_month = current_date.month - 1 or 12
    previous_year = (
        current_date.year if current_date.month != 1 else current_date.year - 1
    )
    return previous_year, previous_month


def set_next_month(date: datetime):
    return (date + relativedelta(months=1)).strftime("%Y-%m-%d")
