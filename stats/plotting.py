import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from db.db_operations import fetch_expense
from utils.validation import beautify_data, analyze_beautify

sns.set_theme()


class Plotting:
    def __init__(self):
        self.df = self._create_df()

    def expense_plot(self):
        """
        Creates and displays an average expense plot for all the data in the database.
        :return: This function does not return anything
        """
        avg = self.df.groupby("year")["amount"].mean().reset_index()
        sns.lineplot(data=avg, x="year", y="amount")
        plt.title("Average spending per year")
        plt.xlabel("Year")
        plt.ylabel("Avg spending")
        plt.show()

    def expense_month_year_distribution(self, year):
        """
        Plots the distribution of avg expense per month in a specified year
        :param year: Specifies the year for which we want to see the yearly expense distribution
        :return: This function does not return anything
        """
        filtered_df = self.df[self.df["year"] == int(year)]
        avg = filtered_df.groupby(["month", "category"])["amount"].mean().reset_index()
        sns.barplot(data=avg, x="month", y="amount", hue="category")
        plt.title(f"Distribution of expenses through the year {year}")
        plt.xlabel("Month")
        plt.ylabel("Avg expense amount")
        plt.show()

    def monthly_expense(self, year, month):
        """
        Plots the distribution of expenses for a given month and year
        :param year: Describes the year used for analysis
        :param month: Describes the month we want to create plot for
        :return: This function does not return anything
        """
        filtered_df = self.df[self.df["year"] == int(year)]
        avg = filtered_df.groupby(["month", "category"])["amount"].mean().reset_index()
        avg = avg[avg["month"] == int(month)]
        sns.barplot(data=avg, x="month", y="amount", hue="category")
        plt.show()

    def _create_df(self):
        df = pd.DataFrame(
            list(map(beautify_data, fetch_expense())),
            columns=["category", "amount", "description", "date"],
        )
        df["amount"] = df["amount"].astype(float)
        df["date"] = pd.to_datetime(df["date"])
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        return df
