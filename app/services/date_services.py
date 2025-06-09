from datetime import datetime


def get_previous_month() -> tuple:
    current_date = datetime.now()
    previous_month = current_date.month - 1 or 12
    previous_year = (
        current_date.year if current_date.month != 1 else current_date.year - 1
    )
    return previous_year, previous_month


def parse_date(year: int, month: int) -> str:
    """
    :param year: Int value for year
    :param month: Int value for month
    :return: date in format YYYY-MM
    """
    return f"{year}-{int(month):02d}"
