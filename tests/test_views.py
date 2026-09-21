import pandas as pd

from src.views import (
    get_card_statistics,
    get_greeting,
    get_top_transactions,
    main_page,
    get_expenses_income,
    get_top_categories,
    get_cashback_by_category,
    search_transactions,
    search_transactions_by_phone
)
from unittest.mock import Mock, patch
from src.views import get_currency_rates



def test_greeting_morning():
    assert get_greeting("2021-12-31 06:00:00") == "Доброе утро"
    assert get_greeting("2021-12-31 11:59:59") == "Доброе утро"


def test_greeting_day():
    assert get_greeting("2021-12-31 12:00:00") == "Добрый день"
    assert get_greeting("2021-12-31 17:59:59") == "Добрый день"


def test_greeting_evening():
    assert get_greeting("2021-12-31 18:00:00") == "Добрый вечер"
    assert get_greeting("2021-12-31 22:59:59") == "Добрый вечер"


def test_greeting_night():
    assert get_greeting("2021-12-31 23:00:00") == "Доброй ночи"
    assert get_greeting("2021-12-31 05:59:59") == "Доброй ночи"


def test_get_card_statistics():
    transactions = pd.DataFrame(
        {
            "Номер карты": ["*7197", "*7197", "*5091", "*5091"],
            "Сумма операции": [-150.0, -250.0, -99.0, -101.0],
        }
    )

    result = get_card_statistics(transactions)

    assert result == [
        {
            "last_digits": "7197",
            "total_spent": 400.0,
            "cashback": 4.0,
        },
        {
            "last_digits": "5091",
            "total_spent": 200.0,
            "cashback": 2.0,
        },
    ]


def test_get_top_transactions():
    transactions = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                [
                    "01.12.2021 10:00:00",
                    "02.12.2021 10:00:00",
                    "03.12.2021 10:00:00",
                    "04.12.2021 10:00:00",
                    "05.12.2021 10:00:00",
                    "06.12.2021 10:00:00",
                ],
                format="%d.%m.%Y %H:%M:%S",
            ),
            "Сумма операции": [
                -100.0,
                -500.0,
                -300.0,
                -1000.0,
                -200.0,
                -50.0,
            ],
            "Категория": [
                "Еда",
                "Транспорт",
                "Еда",
                "Одежда",
                "Связь",
                "Еда",
            ],
            "Описание": [
                "Покупка 1",
                "Покупка 2",
                "Покупка 3",
                "Покупка 4",
                "Покупка 5",
                "Покупка 6",
            ],
        }
    )

    result = get_top_transactions(transactions)

    assert len(result) == 5

    assert result == [
        {
            "date": "04.12.2021",
            "amount": 1000.0,
            "category": "Одежда",
            "description": "Покупка 4",
        },
        {
            "date": "02.12.2021",
            "amount": 500.0,
            "category": "Транспорт",
            "description": "Покупка 2",
        },
        {
            "date": "03.12.2021",
            "amount": 300.0,
            "category": "Еда",
            "description": "Покупка 3",
        },
        {
            "date": "05.12.2021",
            "amount": 200.0,
            "category": "Связь",
            "description": "Покупка 5",
        },
        {
            "date": "01.12.2021",
            "amount": 100.0,
            "category": "Еда",
            "description": "Покупка 1",
        },
    ]


@patch("src.views.requests.get")
def test_get_currency_rates(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {
        "base": "USD",
        "quote": "RUB",
        "rate": 80.5,
    }
    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    result = get_currency_rates(["USD"])

    assert result == [
        {
            "currency": "USD",
            "rate": 80.5,
        }
    ]

    mock_get.assert_called_once_with(
        "https://api.frankfurter.dev/v2/rate/USD/RUB",
        timeout=10,
    )


from unittest.mock import Mock, patch


@patch("src.views.requests.get")
def test_get_currency_rates_multiple(mock_get):
    responses = [
        {"rate": 80.5},
        {"rate": 93.2},
    ]

    mock_get.side_effect = [
        Mock(
            json=Mock(return_value=responses[0]),
            raise_for_status=Mock(),
        ),
        Mock(
            json=Mock(return_value=responses[1]),
            raise_for_status=Mock(),
        ),
    ]

    result = get_currency_rates(["USD", "EUR"])

    assert result == [
        {
            "currency": "USD",
            "rate": 80.5,
        },
        {
            "currency": "EUR",
            "rate": 93.2,
        },
    ]

from src.views import get_stock_prices


@patch("src.views.requests.get")
def test_get_stock_prices(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {
        "Global Quote": {
            "05. price": "250.50"
        }
    }

    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    result = get_stock_prices(["AAPL"])

    assert result == [
        {
            "stock": "AAPL",
            "price": 250.5,
        }
    ]


@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
def test_main_page(mock_currency_rates, mock_stock_prices):
    transactions = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                [
                    "01.12.2021 10:00:00",
                    "15.12.2021 12:00:00",
                    "20.12.2021 18:00:00",
                    "31.12.2021 23:00:00",
                    "01.01.2022 10:00:00",
                ],
                format="%d.%m.%Y %H:%M:%S",
            ),
            "Статус": [
                "OK",
                "OK",
                "OK",
                "OK",
                "OK",
            ],
            "Номер карты": [
                "*7197",
                "*7197",
                "*5091",
                "*5091",
                "*7197",
            ],
            "Сумма операции": [
                -100.0,
                -500.0,
                -200.0,
                -1000.0,
                -9999.0,
            ],
            "Категория": [
                "Еда",
                "Одежда",
                "Транспорт",
                "Жильё",
                "Еда",
            ],
            "Описание": [
                "Покупка 1",
                "Покупка 2",
                "Покупка 3",
                "Покупка 4",
                "Покупка 5",
            ],
            "Кэшбэк": [
                10.0,
                20.0,
                5.0,
                30.0,
                50.0,
            ],
        }
    )

    mock_currency_rates.return_value = [
        {"currency": "USD", "rate": 80.0},
        {"currency": "EUR", "rate": 90.0},
    ]

    mock_stock_prices.return_value = [
        {"stock": "AAPL", "price": 200.0},
        {"stock": "AMZN", "price": 250.0},
        {"stock": "GOOGL", "price": 300.0},
        {"stock": "MSFT", "price": 400.0},
        {"stock": "TSLA", "price": 500.0},
    ]

    result = main_page(
        "2021-12-31 23:59:59",
        transactions,
    )

    assert result["greeting"] == "Доброй ночи"

    assert len(result["cards"]) == 2

    assert len(result["top_transactions"]) == 4

    assert result["currency_rates"] == [
        {"currency": "USD", "rate": 80.0},
        {"currency": "EUR", "rate": 90.0},
    ]

    assert len(result["stock_prices"]) == 5

    assert result["top_transactions"][0]["amount"] == 1000.0

    assert all(
        transaction["date"].endswith(".12.2021")
        for transaction in result["top_transactions"]
    )
    assert "top_categories" in result
    assert "cashback" in result

def test_get_expenses_income():
    transactions = pd.DataFrame(
        {
            "Статус": ["OK", "OK", "OK", "OK"],
            "Сумма операции": [
                -100.40,
                -200.60,
                500.40,
                300.60,
            ],
            "Категория": [
                "Супермаркеты",
                "Супермаркеты",
                "Зарплата",
                "Зарплата",
            ],
        }
    )

    expenses, income = get_expenses_income(transactions)

    assert expenses == {
        "total_amount": 301,
        "main": [
            {
                "category": "Супермаркеты",
                "amount": 301,
            }
        ],
    }

    assert income == {
        "total_amount": 801,
        "main": [
            {
                "category": "Зарплата",
                "amount": 801,
            }
        ],
    }


def test_get_top_categories():
    transactions = pd.DataFrame(
        {
            "Статус": ["OK"] * 11,
            "Сумма операции": [
                -1000,
                -900,
                -800,
                -700,
                -600,
                -500,
                -400,
                -300,
                -200,
                -150,
                -250,
            ],
            "Категория": [
                "Категория 1",
                "Категория 2",
                "Категория 3",
                "Категория 4",
                "Категория 5",
                "Категория 6",
                "Категория 7",
                "Категория 8",
                "Категория 9",
                "Переводы",
                "Другая",
            ],
            "Описание": [
                "Покупка",
                "Покупка",
                "Покупка",
                "Покупка",
                "Покупка",
                "Покупка",
                "Покупка",
                "Покупка",
                "Покупка",
                "Перевод",
                "Покупка",
            ],
        }
    )

    result = get_top_categories(transactions)

    assert result == [
        {"category": "Категория 1", "amount": 1000},
        {"category": "Категория 2", "amount": 900},
        {"category": "Категория 3", "amount": 800},
        {"category": "Категория 4", "amount": 700},
        {"category": "Категория 5", "amount": 600},
        {"category": "Категория 6", "amount": 500},
        {"category": "Категория 7", "amount": 400},
        {"category": "Остальное", "amount": 750},
        {"category": "Переводы", "amount": 150},
    ]


def test_get_top_categories_cash():
    transactions = pd.DataFrame(
        {
            "Статус": ["OK", "OK"],
            "Сумма операции": [-1000, -500],
            "Категория": ["Супермаркеты", None],
            "Описание": [
                "Покупка продуктов",
                "Снятие наличных в банкомате",
            ],
        }
    )

    result = get_top_categories(transactions)

    assert result == [
        {"category": "Супермаркеты", "amount": 1000},
        {"category": "Наличные", "amount": 500},
    ]


def test_get_top_categories_ignores_failed():
    transactions = pd.DataFrame(
        {
            "Статус": ["OK", "FAILED"],
            "Сумма операции": [-100, -5000],
            "Категория": ["Еда", "Супермаркеты"],
            "Описание": ["Покупка", "Покупка"],
        }
    )

    result = get_top_categories(transactions)

    assert result == [
        {"category": "Еда", "amount": 100},
    ]


def test_get_cashback_by_category():
    transactions = pd.DataFrame(
        {
            "Статус": [
                "OK",
                "OK",
                "OK",
                "OK",
                "OK",
                "FAILED",
            ],
            "Сумма операции": [
                -1000,
                -2000,
                -3000,
                -4000,
                -5000,
                -10000,
            ],
            "Категория": [
                "Еда",
                "Еда",
                "Супермаркеты",
                "Транспорт",
                "Развлечения",
                "Супермаркеты",
            ],
            "Кэшбэк": [
                10,
                25,
                50,
                30,
                5,
                100,
            ],
        }
    )

    result = get_cashback_by_category(transactions)

    assert result == [
        {"category": "Супермаркеты", "cashback": 50.0},
        {"category": "Еда", "cashback": 35.0},
        {"category": "Транспорт", "cashback": 30.0},
    ]


def test_get_cashback_by_category_less_than_three():
    transactions = pd.DataFrame(
        {
            "Статус": ["OK", "OK"],
            "Сумма операции": [-1000, -2000],
            "Категория": ["Еда", "Еда"],
            "Кэшбэк": [10, 20],
        }
    )

    result = get_cashback_by_category(transactions)

    assert result == [
        {"category": "Еда", "cashback": 30.0},
    ]

def test_search_transactions_case_insensitive():
    transactions = pd.DataFrame(
        {
            "Категория": [
                "Супермаркеты",
                "Фастфуд",
                "СУПЕРМАРКЕТЫ",
                "Транспорт",
            ],
            "Описание": [
                "Покупка продуктов",
                "Бургер",
                "Покупка",
                "Билет",
            ],
            "Сумма операции": [-100, -200, -300, -400],
        }
    )

    result = search_transactions(transactions, "супермар")

    assert len(result) == 2
    assert result["Категория"].tolist() == [
        "Супермаркеты",
        "СУПЕРМАРКЕТЫ",
    ]


def test_search_transactions_substring():
    transactions = pd.DataFrame(
        {
            "Категория": [
                "Мобильная связь",
                "Транспорт",
                "Связь",
            ],
            "Описание": [
                "Оплата телефона",
                "Метро",
                "Оплата услуг",
            ],
        }
    )

    result = search_transactions(transactions, "связ")

    assert len(result) == 2


def test_search_transactions_no_results():
    transactions = pd.DataFrame(
        {
            "Категория": ["Еда", "Транспорт"],
            "Описание": ["Кафе", "Метро"],
        }
    )

    result = search_transactions(transactions, "авиабилеты")

    assert result.empty


def test_search_transactions_by_phone():
    transactions = pd.DataFrame(
        {
            "Описание": [
                "Перевод на номер +7 (900) 000-00-00",
                "Перевод на номер 89000000000",
                "Перевод на номер +79001112233",
                "Покупка в магазине",
            ],
            "Сумма операции": [-100, -200, -300, -400],
        }
    )

    result = search_transactions_by_phone(
        transactions,
        "+7 (900) 000-00-00",
    )

    assert len(result) == 2
    assert result["Сумма операции"].tolist() == [-100, -200]


def test_search_transactions_by_phone_from_8_format():
    transactions = pd.DataFrame(
        {
            "Описание": [
                "Перевод +7 (900) 000-00-00",
                "Перевод 89000000000",
                "Перевод +7 (901) 111-22-33",
            ],
        }
    )

    result = search_transactions_by_phone(
        transactions,
        "89000000000",
    )

    assert len(result) == 2


def test_search_transactions_by_phone_no_results():
    transactions = pd.DataFrame(
        {
            "Описание": [
                "Перевод +7 (900) 000-00-00",
                "Перевод +7 (901) 111-22-33",
            ],
        }
    )

    result = search_transactions_by_phone(
        transactions,
        "89223334455",
    )

    assert result.empty