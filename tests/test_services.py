from src.services import investment_bank
import pytest

def test_investment_bank():
    transactions = [
        {
            "Дата операции": "2021-12-10",
            "Статус": "OK",
            "Сумма операции": -1712.00,
        },
        {
            "Дата операции": "2021-12-15",
            "Статус": "OK",
            "Сумма операции": -1234.00,
        },
    ]

    result = investment_bank("2021-12", transactions, 50)

    assert result == 54


def test_investment_bank_ignores_other_month():
    transactions = [
        {
            "Дата операции": "2021-11-10",
            "Статус": "OK",
            "Сумма операции": -1712,
        },
    ]

    assert investment_bank("2021-12", transactions, 50) == 0


def test_investment_bank_ignores_income():
    transactions = [
        {
            "Дата операции": "2021-12-10",
            "Статус": "OK",
            "Сумма операции": 174000,
        },
    ]

    assert investment_bank("2021-12", transactions, 50) == 0


def test_investment_bank_ignores_failed_transactions():
    transactions = [
        {
            "Дата операции": "2021-12-10",
            "Статус": "FAILED",
            "Сумма операции": -1712,
        },
    ]

    assert investment_bank("2021-12", transactions, 50) == 0


def test_investment_bank_zero_amount():
    transactions = [
        {
            "Дата операции": "2021-12-10",
            "Статус": "OK",
            "Сумма операции": 0,
        },
    ]

    assert investment_bank("2021-12", transactions, 50) == 0


def test_investment_bank_different_limits():
    transactions = [
        {
            "Дата операции": "2021-12-10",
            "Статус": "OK",
            "Сумма операции": -1712,
        },
    ]

    assert investment_bank("2021-12", transactions, 10) == 8
    assert investment_bank("2021-12", transactions, 50) == 38
    assert investment_bank("2021-12", transactions, 100) == 88





def test_investment_bank_invalid_limit():
    with pytest.raises(ValueError):
        investment_bank("2021-12", [], 25)