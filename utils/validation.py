from datetime import datetime
from calendar import monthrange


def validate_year(data: int) -> bool:
    available_years = list(range(2005, 2025))
    if data in available_years:
        return True
    else:
        print(f"Invalid year. Choose from: {available_years}")


def validate_date(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except Exception as e:
        print(f"Exception {e} occurred. Date must be in the format YYYY-MM-DD")


def validate_month(data: int) -> bool:
    available_months = list(range(1, 13))
    if data in available_months:
        return True
    else:
        print("Invalid month, please enter a month number from range 1 to 12")


def get_amount_input() -> float:
    while True:
        amount = input("Enter a valid amount: ")
        try:
            amount = round(float(amount.replace(",", ".")), 2)
            if amount <= 0:
                print("Amount must be greater than 0!")
                continue
            return amount
        except ValueError:
            print("\nThat is not a valid number, try again!")


def beautify_data(data) -> tuple:
    try:
        _, name, amount, description, date = data
        cleaned_amount = float(amount)
        cleaned_date = datetime.strptime(str(date), "%Y-%m-%d").date() if date else None
        cleaned_record = (name, cleaned_amount, description, cleaned_date)
        return cleaned_record
    except ValueError as e:
        print(f"Error converting data: {e}")
        return ()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return ()


def analyze_beautify(data) -> tuple:
    try:
        amount, name = data
        cleaned_amount = float(amount)
        cleaned_record = (name, cleaned_amount)
        return cleaned_record
    except ValueError as e:
        print(f"Error converting data: {e}")
        return ()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return ()


def category_input() -> str:
    while True:
        category = input(
            "Select a category from available ones: \n "
            'Food & Groceries", "Transportation", "Housing", "Entertainment", "Misc '
        )
        if category in [
            "Food & Groceries",
            "Transportation",
            "Housing",
            "Entertainment",
            "Misc",
        ]:
            return category
        else:
            print("Invalid choice, pick again")
            continue


def year_input():
    while True:
        expense_year = input("Select year: ")
        try:
            expense_year = int(expense_year)
            if validate_year(expense_year):
                return expense_year
        except ValueError:
            print("The year has to be a number!")


def month_input():
    expense_month = input("Select month: ")
    try:
        expense_month = int(expense_month)
        if validate_month(expense_month):
            return expense_month
    except ValueError:
        print("The month has to be a number")


def day_input(year, month):
    _, month_len = monthrange(year, month)
    while True:
        expense_day = input("Select day: ")
        try:
            expense_day = int(expense_day)
            if 0 < expense_day <= month_len:
                return expense_day
        except ValueError:
            print(f"Day has to be a number lower than {month_len}")


def date_input() -> str:
    year = year_input()
    month = month_input()
    day = day_input(year, month)
    return f"{year}-{month:02d}-{day:02d}"
