import re
from datetime import datetime
from utils.helpers import get_budget_for_user


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
    required_fields = ["category_id", "amount", "expense_date"]
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
    return 1 <= budget.status_id <= 4


def is_valid_category(cat_id) -> bool:
    try:
        cat_id = int(cat_id)
        return 1 <= cat_id <= 5
    except (ValueError, TypeError):
        return False


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
            return False, "Incorrect year format, try again"
        if not is_valid_month(data["budget_month"]):
            return False, "Incorrect month format, try again"
    return True, None


def validate_expense_edit(data, is_patch=False):
    allowed_fields = [
        "category_id",
        "amount",
        "description",
        "expense_date",
        "is_cyclical",
    ]
    required_fields = ["category_id", "amount", "expense_date"]
    errors = {}
    check_new_budget_id = False

    unknown_fields = [field for field in data if field not in allowed_fields]
    if unknown_fields:
        errors["unknown_fields"] = f"Fields {unknown_fields} not allowed in this call"

    if not is_patch:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            errors["missing_fields"] = f"Missing required fields {missing_fields}"
        is_valid, error_msg = validate_expense(data)
        if not is_valid:
            errors["Validation"] = error_msg

    if "expense_date" in data:
        check_new_budget_id = True
        if not is_valid_date(data["expense_date"]):
            errors["date"] = "Incorrect date format"

    if "amount" in data:
        if not is_valid_amount(data["amount"]):
            errors["amount"] = "Incorrect value passed as amount"

    if "category_id" in data:
        if not is_valid_category(data["category_id"]):
            errors["category_id"] = "Incorrect category id passed"

    if errors:
        return False, check_new_budget_id, errors
    return True, check_new_budget_id, errors


def validate_income(data):
    required_fields = ["category_id", "amount", "income_date", "is_cyclical"]
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    if not is_valid_amount(data["amount"]):
        return False, f"Incorrect value passed as amount"
    if not is_valid_date(data["income_date"]):
        return False, f"Incorrect date format"
    try:
        data["category_id"] = int(data["category_id"])
        return 1 <= data["category_id"] <= 4
    except (ValueError, TypeError):
        return False


def validate_income_edit(data, is_patch=False):
    required_fields = ["category_id", "amount", "income_date", "is_cyclical"]
    errors = {}
    check_new_budget_id = False

    unknown_fields = [field for field in data if field not in required_fields]
    if unknown_fields:
        errors["unknown_fields"] = f"Fields {unknown_fields} not editable"

    if not is_patch:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            errors["missing_fields"] = f"Missing required fields {missing_fields}"
        is_valid, error_msg = validate_income(data)
        if not is_valid:
            errors["Validation"] = error_msg

    if "income_date" in data:
        check_new_budget_id = True
        if not is_valid_date(data["income_date"]):
            errors["date"] = "Incorrect date format"

    if "amount" in data:
        if not is_valid_amount(data["amount"]):
            errors["amount"] = "Incorrect value passed as amount"

    if "category_id" in data:
        if not is_valid_category(data["category_id"]):
            errors["category_id"] = "Incorrect category id passed"

    if errors:
        return False, check_new_budget_id, errors
    return True, check_new_budget_id, errors
