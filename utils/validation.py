from datetime import datetime


class Validation:
    @staticmethod
    def validate_year(data):
        available_years = list(range(2005, 2025))
        if data not in available_years:
            raise ValueError(f"Invalid year. Choose from: {available_years}")

    @staticmethod
    def validate_date(date):
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in the format YYYY-MM-DD")

    @staticmethod
    def validate_month(data):
        available_months = {
            "January": 1,
            "February": 2,
            "March": 3,
            "April": 4,
            "May": 5,
            "June": 6,
            "July": 7,
            "August": 8,
            "September": 9,
            "October": 10,
            "November": 11,
            "December": 12,
        }
        # ---WORK IN PROGRESS---
