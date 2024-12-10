from datetime import datetime


class Validation:
    @staticmethod
    def validate_year(data):
        pass

    @staticmethod
    def validate_date(date):
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Date must be in the format YYYY-MM-DD')

