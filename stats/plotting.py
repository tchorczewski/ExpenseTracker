import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme()


class Plotting:
    def __init__(self):
        self._dir = os.path.dirname(os.path.abspath(__file__))
        self._root_dir = os.path.dirname(self._dir)
        self.data_file_path = os.path.join(self._root_dir, 'data.json')
        self.df = pd.read_json(self.data_file_path).transpose()
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df['amount'] = pd.to_numeric(self.df['amount'])
        self.df = self.df.sort_values(by=['date'])
        self.df['year'] = self.df['date'].dt.year
        self.df['month'] = self.df['date'].dt.month

    def expense_plot(self):
        """
        Creates and displays an average expense plot for all the data in the database.
        :return: This function does not return anything
        """
        avg = self.df.groupby('year')['amount'].mean().reset_index()
        sns.lineplot(data=avg, x='year', y='amount')
        plt.title('Average spending per year')
        plt.xlabel('Avg spending amount')
        plt.show()

    def expense_month_year_distribution(self, year):
        """
        Plots the distribution of avg expense per month in a specified year
        :param year: Specifies the year for which we want to see the yearly expense distribution
        :return: This function does not return anything
        """
        filtered_df = self.df[self.df['year'] == int(year)]
        avg = filtered_df.groupby(['month', 'category'])['amount'].mean().reset_index()
        sns.barplot(data=avg, x='month', y='amount', hue='category')
        plt.title(f'Distribution of expenses through the year {year}')
        plt.xlabel('Month')
        plt.ylabel('Avg expense amount')
        plt.show()

    def monthly_expense(self, year, month):
        """
        Plots the distribution of expenses for a given month and year
        :param year: Describes the year used for analysis
        :param month: Describes the month we want to create plot for
        :return: This function does not return anything
        """
        filtered_df = self.df[self.df['year'] == int(year)]
        avg = filtered_df.groupby(['month', 'category'])['amount'].mean().reset_index()
        avg = avg[avg['month'] == int(month)]
        sns.barplot(data=avg, x='month', y='amount', hue='category')
        plt.show()
