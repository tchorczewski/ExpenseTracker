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


def validate_expense(data) -> (bool, str):
    """
    Validation method used when creating expenses via API.
    :param data: Data from a create_expense request
    :return: A boolean value if the validation is OK, additional error message to inform where the issue is
    """
    required_fields = ["category_id", "amount", "expense_date, budget_id"]
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    if not isinstance(data["amount"], (int, float)) or data["amount"] <= 0:
        return False, "Incorrect value passed as amount"
    if not is_valid_date(data["expense_date"]):
        return False, "Incorrect date format, should be YYYY-MM-DD"
    if not is_valid_category(data["category_id"]):
        return False, "Out of category scope for expenses please call the developer"
    return True, None


def is_valid_category(cat_id):
    return isinstance(cat_id, int) and cat_id in range(1, 6)


def validate_budget(data) -> (bool, str):
    pass
