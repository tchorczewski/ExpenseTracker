from datetime import datetime


def get_current_date():
    current_date = datetime.now()
    return current_date.year, current_date.month


def parse_date(year, month) -> str:
    """
    There is no need to validate data as it will be done on an earlier step
    :param year: Year from the request
    :param month: Month from the request
    :return: date in format YYYY-MM
    """
    return f"{year}-{int(month):02d}"
