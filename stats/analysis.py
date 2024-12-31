def total_sum(data):
    return sum(amount for _, amount, _, _ in data)


def conditional_sum(data):
    return sum(amount for amount, _ in data)


def compare_years(year_1, year_2):
    if year_1 == year_2:
        return f"Equal"
    else:
        return f"{year_1 if year_1 > year_2 else year_2}"


def compare_month(month_1, month_2):
    if month_1 == month_2:
        return f"Equal"
    else:
        return f"{month_1 if month_1 > month_2 else month_2}"
