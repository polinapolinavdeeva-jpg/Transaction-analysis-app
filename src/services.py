from typing import Any
import math


def investment_bank(
    month: str,
    transactions: list[dict[str, Any]],
    limit: int,
) -> float:
    """Рассчитывает сумму для копилки за указанный месяц."""

    if limit not in (10, 50, 100):
        raise ValueError("Некорректный лимит")

    total = 0.0

    for transaction in transactions:
        if transaction["Статус"] != "OK":
            continue

        if not transaction["Дата операции"].startswith(month):
            continue

        amount = float(transaction["Сумма операции"])

        if amount >= 0:
            continue

        expense = abs(amount)
        rounded_expense = math.ceil(expense / limit) * limit

        total += rounded_expense - expense

    return round(total, 2)