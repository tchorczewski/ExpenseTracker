from expense import Expense

r1 = Expense()

r1.amount = 150
r1.date = '2024-05-06'
r1.category = 'Electricity'

print(r1)

r2 = Expense(220)

print(Expense.compare_amounts(r1, '^', r2))
