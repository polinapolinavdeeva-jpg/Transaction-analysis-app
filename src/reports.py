import json
from functools import wraps
from typing import Callable, Optional
from datetime import datetime


import pandas as pd



def report(
    func: Optional[Callable] = None,
    filename: Optional[str] = None,
):
    """Декоратор для сохранения результата отчёта в JSON."""

    if isinstance(func, str):
        filename = func
        func = None

    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)

            output_filename = filename or "report.json"

            if isinstance(result, pd.DataFrame):
                data = result.to_dict(orient="records")
            else:
                data = result

            with open(
                output_filename,
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4,
                    default=str,
                )

            return result

        return wrapper

    if func is not None:
        return decorator(func)

    return decorator


@report
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: Optional[str] = None,
) -> pd.DataFrame:
    """Возвращает расходы выбранной категории за последние три месяца."""

    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, "%Y-%m-%d")

    end_date = end_date.replace(
        hour=23,
        minute=59,
        second=59,
    )

    start_date = (
        end_date - pd.DateOffset(months=2)
    ).replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
    )

    result = transactions[
        (transactions["Категория"] == category)
        & (transactions["Сумма операции"] < 0)
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
    ]

    return result.copy()

