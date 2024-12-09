from datetime import datetime

class Analysis:
    def __init__(self, items=None):
        if items is None:
            items = []
        self._items = items

    def total_sum(self):
        if not self._items:
            print('No values to sum, please fill the data')
        else:
            return sum(float(item['amount']) for item in self._items)

    def sum_month(self, month):
        if isinstance(month,int):
            current_month_expenses = [float(item['amount']) for item in self._items if int(datetime.strptime(item['date'], '%Y-%m-%d').month) == month]
            return sum(current_month_expenses)
        else:
            print('Inserted incorrect value,please try again')

    def sum_year(self, year):
        if isinstance(year, int) and year <= int(datetime.now().year):
            year_expenses = [float(item['amount']) for item in self._items if int(datetime.strptime(item['date'],
                                                                                                format('%Y-%m-%d')).year) == year]
            return sum(year_expenses)
        else:
            print('Inserted incorrect value,please try again')

