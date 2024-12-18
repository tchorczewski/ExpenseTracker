from datetime import datetime


class Analysis:
    def __init__(self, items: list = None):
        if items is None:
            items = []
        self._items = items

    def total_sum(self):
        if not self._items:
            print("No values to sum, please fill the data")
        else:
            return sum(float(amount) for _, amount, _, _ in self._items)

    def sum_month(self, month):
        if isinstance(month, int):
            current_month_expenses = [
                float(amount)
                for _, amount, _, date in self._items
                if int(datetime.strptime(date, "%Y-%m-%d").month) == month
            ]
            return sum(current_month_expenses)
        else:
            print("Inserted incorrect value,please try again")

    def sum_year(self, year):
        if isinstance(year, int) and year <= int(datetime.now().year):
            year_expenses = [
                float(amount)
                for _, amount, _, date in self._items
                if int(datetime.strptime(date, "%Y-%m-%d").year) == year
            ]
            return sum(year_expenses)
        else:
            print("Inserted incorrect value,please try again")
