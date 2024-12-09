import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()

class Plotting:
    def __init__(self):
        self.df = pd.read_json('data.json').transpose()
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['amount'] = pd.to_numeric(self.df['amount'])

    def expense_plot(self):
        self.df = self.df.sort_values(by=['date'])
        self.df['year'] = self.df['date'].dt.year
        avg = self.df.groupby('year')['amount'].mean().reset_index()
        sns.lineplot(data=avg, x='year', y='amount')
        plt.title('Average spending per year')
        plt.xlabel('Avg spending amount')
        plt.show()
