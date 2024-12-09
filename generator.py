import random
from datetime import datetime,timedelta

from expense import Expense
from expensemanager import ExpenseManager

categories = ["Food & Groceries", "Transportation", "Housing", "Entertainment", "Misc"]
em = ExpenseManager()

for i in range(5000):
    random_num = random.randint(0,4)
    amount = round(random.uniform(1, 5999.99), 2)
    category = categories[random_num]
    date = (datetime(2005, 1, 1) + timedelta(days=random.randint(0, (datetime(2024, 12, 31) - datetime(2005, 1, 1)).days))).date()
    ex = Expense(amount,category,date)
    em.partial_save(ex)
