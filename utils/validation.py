import re
from datetime import datetime
from app.services.budget_services import check_if_budget_exists


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


def is_valid_type(transaction_type) -> bool:
    return transaction_type in ["expense", "income"]


def validate_transaction(data):
    """
    Validate if passed data is going to create valid transaction
    :param data: Data from request
    :return: A boolean value if the validation is OK, additional error message or none if okay
    """
    required_fields = [
        "category_id",
        "amount",
        "date",
        "is_cyclical",
        "budget_id",
        "type",
    ]
    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"Missing required field: {field}"
    if not is_valid_amount(data["amount"]):
        return False, "Incorrect value passed as amount"
    if not is_valid_date(data["date"]):
        return False, "Incorrect date format, should be YYYY-MM-DD"
    if not is_valid_type(data["type"]):
        return False, "Incorrect transaction type"
    if not check_if_budget_exists(data["budget_id"]):
        return False, "Budget does not exist"

    return True, None


def validate_budget(data):
    """
    Takes the raw data from requests and checks for required fields that user has to fill and verifies the integrity of the data.
    :param data: Raw data from the API request
    :return: Tuple (Bool, error_msg) Bool of the validity check and error message if applicable
    """
    required_fields = ["budget_month", "budget_year", "amount"]
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
        if not is_valid_amount(data["amount"]):
            return False, "Incorrect value passed as amount"
        if not is_valid_year(data["budget_year"]):
            return False, "Incorrect data"
        if not is_valid_month(data["budget_month"]):
            return False, "Incorrect data"
    return True, None


def validate_transaction_edit(data):
    allowed_fields = ["id", "category_id", "amount", "date", "is_cyclical", "type"]
    errors = {}
    unknown_fields = [field for field in data if field not in allowed_fields]
    if unknown_fields:
        errors["unknown_fields"] = f"Fields {unknown_fields} not allowed in this call"

    if "amount" in data:
        if not is_valid_amount(data["amount"]):
            errors["amount"] = "Incorrect value passed as amount"
    if "type" in data:
        if not is_valid_type(data["type"]):
            errors["type"] = "Incorrect transaction type"
    if errors:
        return False, errors
    return True, errors


def validate_budget_edit(data):
    editable_fields = {"id", "status_id", "amount", "budget_year", "budget_month"}
    errors = {}

    unknown_fields = [f for f in data if f not in editable_fields]
    if unknown_fields:
        errors["unknown_fields"] = f"Fields {unknown_fields} not editable"

    if "amount" in data and not is_valid_amount(data["amount"]):
        errors["amount"] = "Incorrect amount format"
    if "budget_month" in data and not is_valid_month(data["budget_month"]):
        errors["month"] = "Invalid month"
    if "budget_year" in data and not is_valid_year(data["budget_year"]):
        errors["year"] = (
            f"Invalid year (should be between 1922 and {datetime.now().year + 10})"
        )

    if errors:
        return False, errors
    return True, {}


def validate_register(data):
    errors = {}
    required_fields = ["username", "first_name", "last_name", "email", "password"]
    for field in data:
        if field not in required_fields:
            errors["required_fields"] = f"Missing required field: {field}"

    if not is_valid_password(data["password"]):
        errors["password"] = (
            "Password must be at least 8 characters long, contain a number and a letter"
        )
    if not is_valid_email(data["email"]):
        errors["email"] = "Invalid email"
    if errors:
        return False, errors
    return True, {}
