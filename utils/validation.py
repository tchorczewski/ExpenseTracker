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


def is_valid_category(cat_id) -> bool:
    try:
        cat_id = int(cat_id)
        return 1 <= cat_id <= 5
    except (ValueError, TypeError):
        return False


def validate_operation(data):
    """
    Validate if passed data is going to create valid expense/income
    :param data: Data from request
    :return: A boolean value if the validation is OK, additional error message or none if okay
    """
    required_fields = [
        "category_id",
        "amount",
        "date",
        "is_cyclical",
        "budget_id",
    ]
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    if not is_valid_amount(data["amount"]):
        return False, "Incorrect value passed as amount"
    if not is_valid_date(data["date"]):
        return False, "Incorrect date format, should be YYYY-MM-DD"
    if not is_valid_category(int(data["category_id"])):
        return False, "Category not found"

    return True, None


def validate_budget(data):
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
            return False, "Incorrect data"
        if not is_valid_month(data["budget_month"]):
            return False, "Incorrect data"
    return True, None


def validate_operation_edit(data):
    allowed_fields = [
        "category_id",
        "amount",
        "description",
        "date",
        "is_cyclical",
        "expense_id",
        "income_id",
    ]
    errors = {}
    unknown_fields = [field for field in data if field not in allowed_fields]
    if unknown_fields:
        errors["unknown_fields"] = f"Fields {unknown_fields} not allowed in this call"

    if "amount" in data:
        if not is_valid_amount(data["amount"]):
            errors["amount"] = "Incorrect value passed as amount"

    if "category_id" in data:
        if not is_valid_category(data["category_id"]):
            errors["category_id"] = "Incorrect category id passed"

    if errors:
        return False, errors
    return True, errors


def validate_budget_edit(data):
    editable_fields = {"status_id", "budget_amount", "budget_year", "budget_month"}
    errors = {}

    unknown_fields = [f for f in data if f not in editable_fields]
    if unknown_fields:
        errors["unknown_fields"] = f"Fields {unknown_fields} not editable"

    if "budget_amount" in data and not is_valid_amount(data["budget_amount"]):
        errors["amount"] = "Incorrect amount format"
    if "budget_month" in data and not is_valid_month(data["budget_month"]):
        errors["month"] = "Invalid month"
    if "budget_year" in data and not is_valid_year(data["budget_year"]):
        errors["year"] = (
            f"Invalid year (should be between 1922 and {datetime.now().year + 10})"
        )
    if "status_id" in data and not is_valid_category(data["status_id"]):
        errors["status"] = "Invalid or locked status"

    if errors:
        return False, errors
    return True, {}
