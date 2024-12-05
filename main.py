from expense import Expense
from expensemanager import ExpenseManager
from menu import Menu
'''
r1 = Expense()

r1.amount = 1250
r1.date = '2024-05-06'
r1.category = 'Electricity'

j = ExpenseManager()

j.save_data(r1)

data = [j.load_data()]
'''
if __name__ == '__main__':
    menu = Menu()
    menu.main_menu()