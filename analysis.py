from datetime import datetime

class Analysis:
    def __init__(self, items=None):
        if items is None:
            items = []
        self._items = items

    def sum(self):
        if self._items == []:
            print('No values to sum, please fill the data')
        else:
            return sum(float(item['amount']) for item in self._items)

    def sum_month(self):
        current_month = datetime.now().month
        current_month_expenses = [float(item['amount']) for item in self._items if datetime.strptime(item['date'], '%Y-%m-%d').month == current_month]
        return sum(current_month_expenses)

