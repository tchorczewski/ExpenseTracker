from datetime import datetime


def get_previous_month():
    current_date = datetime.now()
    previous_month = current_date.month - 1 or 12
    previous_year = (
        current_date.year if current_date.month != 1 else current_date.year - 1
    )
    return previous_year, previous_month


def parse_date(year, month) -> str:
    """
    There is no need to validate data as it will be done on an earlier step
    :param year: Year from the request
    :param month: Month from the request
    :return: date in format YYYY-MM
    """
    return f"{year}-{int(month):02d}"
