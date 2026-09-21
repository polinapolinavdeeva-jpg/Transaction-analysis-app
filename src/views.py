from datetime import datetime
import time
import pandas as pd
import requests

from src.utils import get_stock_api_key
from src.utils import load_user_settings

def get_greeting(date_time: str) -> str:
    """Возвращает приветствие в зависимости от времени."""

    current_time = datetime.strptime(
        date_time,
        "%Y-%m-%d %H:%M:%S",
    ).time()

    if current_time.hour < 6:
        return "Доброй ночи"

    if current_time.hour < 12:
        return "Доброе утро"

    if current_time.hour < 18:
        return "Добрый день"

    if current_time.hour < 23:
        return "Добрый вечер"

    return "Доброй ночи"


def get_card_statistics(transactions: pd.DataFrame) -> list[dict]:
    """Возвращает статистику расходов по картам."""

    expenses = transactions[
        transactions["Сумма операции"] < 0
    ].copy()

    if expenses.empty:
        return []

    expenses["Расход"] = expenses["Сумма операции"].abs()

    grouped = expenses.groupby(
        "Номер карты",
        sort=False,
    )["Расход"].sum()

    result = []

    for card_number, total_spent in grouped.items():
        result.append(
            {
                "last_digits": str(card_number)[-4:],
                "total_spent": round(float(total_spent), 2),
                "cashback": float(int(total_spent // 100)),
            }
        )

    return result


def get_top_transactions(transactions: pd.DataFrame) -> list[dict]:
    """Возвращает пять крупнейших расходов."""

    expenses = transactions[
        transactions["Сумма операции"] < 0
    ].copy()

    expenses["amount"] = expenses["Сумма операции"].abs()

    top_transactions = expenses.nlargest(
        5,
        "amount",
    )

    result = []

    for _, transaction in top_transactions.iterrows():
        result.append(
            {
                "date": pd.to_datetime(
                    transaction["Дата операции"]
                ).strftime("%d.%m.%Y"),
                "amount": float(transaction["amount"]),
                "category": transaction["Категория"],
                "description": transaction["Описание"],
            }
        )

    return result


def get_currency_rates(currencies: list[str]) -> list[dict]:
    """Возвращает курсы валют к рублю."""

    result = []

    for currency in currencies:
        try:
            url = (
                "https://api.frankfurter.dev/v2/"
                f"rate/{currency}/RUB"
            )

            response = requests.get(
                url,
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()

            result.append(
                {
                    "currency": currency,
                    "rate": float(data["rate"]),
                }
            )

        except (requests.RequestException, KeyError):
            continue

    return result


def filter_transactions_by_date(
    transactions: pd.DataFrame,
    date_time: str,
) -> pd.DataFrame:
    """Оставляет транзакции с начала месяца до указанной даты."""

    end_date = datetime.strptime(
        date_time,
        "%Y-%m-%d %H:%M:%S",
    )

    start_date = end_date.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
    )

    return transactions[
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
    ].copy()


def get_stock_prices(stocks: list[str]) -> list[dict]:
    """Возвращает цены указанных акций."""

    result = []

    for index, stock in enumerate(stocks):
        try:
            if index > 0:
                time.sleep(1)

            url = "https://www.alphavantage.co/query"

            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": stock,
                "apikey": get_stock_api_key(),
            }

            response = requests.get(
                url,
                params=params,
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()
            quote = data.get("Global Quote", {})
            price = quote.get("05. price")

            if price is None:
                continue

            result.append(
                {
                    "stock": stock,
                    "price": float(price),
                }
            )

        except (requests.RequestException, ValueError):
            continue

    return result


def main_page(
    date_time: str,
    transactions: pd.DataFrame,
) -> dict:
    """Формирует данные для главной страницы."""

    settings = load_user_settings()

    filtered_transactions = filter_transactions_by_date(
        transactions,
        date_time,
    )

    expenses, income = get_expenses_income(
        filtered_transactions
    )

    top_categories = get_top_categories(
        filtered_transactions
    )

    cashback = get_cashback_by_category(
        filtered_transactions
    )

    return {
        "greeting": get_greeting(date_time),
        "cards": get_card_statistics(filtered_transactions),
        "top_transactions": get_top_transactions(
            filtered_transactions
        ),
        "expenses": expenses,
        "income": income,
        "top_categories": top_categories,
        "cashback": cashback,
        "currency_rates": get_currency_rates(
            settings["user_currencies"]
        ),
        "stock_prices": get_stock_prices(
            settings["user_stocks"]
        ),
    }


def get_expenses_income(
    transactions: pd.DataFrame,
) -> tuple[dict, dict]:
    """Возвращает статистику расходов и поступлений."""

    expenses = transactions[
        (transactions["Статус"] == "OK")
        & (transactions["Сумма операции"] < 0)
        ].copy()

    income = transactions[
        (transactions["Статус"] == "OK")
        & (transactions["Сумма операции"] > 0)
        ].copy()

    expenses["Сумма"] = expenses["Сумма операции"].abs()

    expenses_grouped = (
        expenses.groupby("Категория")["Сумма"]
        .sum()
        .sort_values(ascending=False)
    )

    income_grouped = (
        income.groupby("Категория")["Сумма операции"]
        .sum()
        .sort_values(ascending=False)
    )

    expenses_result = {
        "total_amount": int(round(expenses["Сумма"].sum())),
        "main": [
            {
                "category": category,
                "amount": int(round(amount)),
            }
            for category, amount in expenses_grouped.items()
        ],
    }

    income_result = {
        "total_amount": int(round(income["Сумма операции"].sum())),
        "main": [
            {
                "category": category,
                "amount": int(round(amount)),
            }
            for category, amount in income_grouped.items()
        ],
    }

    return expenses_result, income_result


def get_top_categories(
    transactions: pd.DataFrame,
) -> list[dict]:
    """Возвращает топ-7 категорий расходов."""

    expenses = transactions[
        (transactions["Статус"] == "OK")
        & (transactions["Сумма операции"] < 0)
    ].copy()

    expenses["Сумма"] = expenses["Сумма операции"].abs()

    # Наличные по описанию операции
    cash_mask = expenses["Описание"].eq("Снятие наличных в банкомате")

    cash_amount = expenses.loc[cash_mask, "Сумма"].sum()

    # Переводы
    transfers_mask = expenses["Категория"].eq("Переводы")

    transfers_amount = expenses.loc[
        transfers_mask,
        "Сумма",
    ].sum()

    # Исключаем специальные категории
    regular_expenses = expenses[
        ~cash_mask & ~transfers_mask
    ].copy()

    # Пустые категории
    regular_expenses = regular_expenses[
        regular_expenses["Категория"].notna()
    ]

    grouped = (
        regular_expenses
        .groupby("Категория")["Сумма"]
        .sum()
        .sort_values(ascending=False)
    )

    top_categories = grouped.head(7)
    other_amount = grouped.iloc[7:].sum()

    result = [
        {
            "category": category,
            "amount": int(round(amount)),
        }
        for category, amount in top_categories.items()
    ]

    if other_amount:
        result.append(
            {
                "category": "Остальное",
                "amount": int(round(other_amount)),
            }
        )

    if transfers_amount:
        result.append(
            {
                "category": "Переводы",
                "amount": int(round(transfers_amount)),
            }
        )

    if cash_amount:
        result.append(
            {
                "category": "Наличные",
                "amount": int(round(cash_amount)),
            }
        )

    return result


def get_cashback_by_category(
    transactions: pd.DataFrame,
) -> list[dict]:
    """Возвращает три категории с наибольшим кешбэком."""

    cashback = transactions[
        (transactions["Статус"] == "OK")
        & (transactions["Сумма операции"] < 0)
        & (transactions["Кэшбэк"] > 0)
    ].copy()

    grouped = (
        cashback.groupby("Категория")["Кэшбэк"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
    )

    return [
        {
            "category": category,
            "cashback": round(float(amount), 2),
        }
        for category, amount in grouped.items()
    ]


def search_transactions(
    transactions: pd.DataFrame,
    query: str,
) -> pd.DataFrame:
    """Ищет операции по подстроке без учета регистра."""
    mask = transactions.astype(str).apply(
        lambda column: column.str.contains(
            query,
            case=False,
            na=False,
            regex=False,
        )
    ).any(axis=1)

    return transactions.loc[mask].copy()


def search_transactions_by_phone(
    transactions: pd.DataFrame,
    phone: str,
) -> pd.DataFrame:
    """Ищет транзакции по номеру телефона в описании."""
    normalized_phone = "".join(
        char for char in phone if char.isdigit()
    )

    if normalized_phone.startswith("8") and len(normalized_phone) == 11:
        normalized_phone = "7" + normalized_phone[1:]

    def normalize_description(value: object) -> str:
        digits = "".join(
            char for char in str(value) if char.isdigit()
        )

        if digits.startswith("8") and len(digits) == 11:
            digits = "7" + digits[1:]

        return digits

    mask = transactions["Описание"].apply(
        normalize_description
    ).str.contains(
        normalized_phone,
        regex=False,
        na=False,
    )

    return transactions.loc[mask].copy()