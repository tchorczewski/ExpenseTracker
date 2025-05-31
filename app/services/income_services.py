from datetime import datetime

from app.services.budget_services import get_budget_for_user


def prepare_income_data(data, user_id):
    data["user_id"] = user_id
    data["amount"] = float(data.get("amount", "0"))
    _, budget, error_msg = get_budget_for_user(user_id, data["income_date"])
    if error_msg:
        return None, f"Something went wrong {error_msg}"
    data["budget_id"] = budget.get("budget_id")
    data["created_at"] = datetime.now().strftime("%Y-%m-%d")
    data["updated_at"] = None
    data["is_cyclical"] = data["is_cyclical"].lower() == "true"
    return data, None
