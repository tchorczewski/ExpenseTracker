import re
from datetime import datetime


def is_valid_email(email) -> bool:
    """
    Checks if e-mail is of valid format
    :param email: E-mail entered by user when registering
    :return: True if e-mail is of valid format
    """
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


def is_valid_password(password) -> bool:
    """
    Checks if password is of given length and contains a char and a digit
    :param password: Not hashed password from before the request is sent
    :return: True if password meets the conditions
    """
    return (
        len(password) >= 8
        and any(c.isdigit() for c in password)
        and any(c.isalpha() for c in password)
    )


def is_valid_date(date) -> bool:
    """
    Checks if date is of valid format.
    :param date: Takes a string date from a request
    :return:
    """
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_year(year) -> bool:
    try:
        year = int(year)
        return 1922 <= year <= datetime.now().year + 10
    except ValueError:
        return False


def is_valid_month(month) -> bool:
    try:
        month = int(month)
        return 1 <= month <= 12
    except ValueError:
        return False


def is_valid_amount(amount) -> bool:
    try:
        amount = float(amount)
        return amount >= 0
    except (ValueError, TypeError):
        return False


def validate_expense(data) -> (bool, str):
    """
    Validation method used when creating expenses via API.
    :param data: Data from a create_expense request
    :return: A boolean value if the validation is OK, additional error message to inform where the issue is
    """
    required_fields = ["category_id", "amount", "expense_date", "budget_id"]
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    if not is_valid_amount(data["amount"]):
        return False, "Incorrect value passed as amount"
    if not is_valid_date(data["expense_date"]):
        return False, "Incorrect date format, should be YYYY-MM-DD"
    if not is_valid_category(int(data["category_id"])):
        return False, "Out of scope for expense categories please contact the developer"
    return True, None


def is_valid_budget_status(budget) -> bool:
    """
    Verifies if the status of a budget is allowing the attempted operation
    :return: True if operation is permitted on given budget
    """
    pass


def is_valid_category(cat_id) -> bool:
    return isinstance(cat_id, int) and cat_id in range(0, 6)


def validate_budget(data) -> (bool, str):
    """
    Takes the raw data from requests and checks for required fields that user has to fill and verifies the integrity of the data.
    :param data: Raw data from the API request
    :return: Tuple (Bool, error_msg) Bool of the validity check and error message if applicable
    """
    required_fields = ["budget_month", "budget_year", "budget_amount"]
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
        if not is_valid_amount(data["budget_amount"]):
            return False, "Incorrect value passed as amount"
        if not is_valid_year(data["budget_year"]):
            return False, f"Incorrect year format, try again"
        if not is_valid_month(data["budget_month"]):
            return False, f"Incorrect month format, try again"
    return True, None
