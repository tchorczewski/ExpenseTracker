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


