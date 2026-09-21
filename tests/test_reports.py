import json
from src.reports import report
import pandas as pd

from src.reports import spending_by_category


def test_spending_by_category():
    transactions = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                [
                    "2021-09-30 10:00:00",
                    "2021-10-01 10:00:00",
                    "2021-11-15 12:00:00",
                    "2021-12-31 16:44:00",
                    "2021-12-20 10:00:00",
                ]
            ),
            "Сумма операции": [
                -100.0,
                -200.0,
                -300.0,
                -400.0,
                -500.0,
            ],
            "Категория": [
                "Супермаркеты",
                "Супермаркеты",
                "Супермаркеты",
                "Супермаркеты",
                "Рестораны",
            ],
        }
    )

    result = spending_by_category(
        transactions,
        "Супермаркеты",
        "2021-12-31",
    )

    assert len(result) == 3
    assert result["Сумма операции"].tolist() == [
        -200.0,
        -300.0,
        -400.0,
    ]


def test_spending_by_category_ignores_income():
    transactions = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                [
                    "2021-12-10 10:00:00",
                    "2021-12-11 10:00:00",
                ]
            ),
            "Сумма операции": [
                -100.0,
                5000.0,
            ],
            "Категория": [
                "Супермаркеты",
                "Супермаркеты",
            ],
        }
    )

    result = spending_by_category(
        transactions,
        "Супермаркеты",
        "2021-12-31",
    )

    assert len(result) == 1
    assert result.iloc[0]["Сумма операции"] == -100.0


def test_spending_by_category_returns_empty_for_unknown_category():
    transactions = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                ["2021-12-10 10:00:00"]
            ),
            "Сумма операции": [-100.0],
            "Категория": ["Супермаркеты"],
        }
    )

    result = spending_by_category(
        transactions,
        "Несуществующая категория",
        "2021-12-31",
    )

    assert result.empty


def test_report_decorator(tmp_path):
    filename = tmp_path / "report.json"

    @report(str(filename))
    def create_report():
        return {"category": "Супермаркеты", "amount": 100}

    result = create_report()

    assert result == {
        "category": "Супермаркеты",
        "amount": 100,
    }

    with open(filename, encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == {
        "category": "Супермаркеты",
        "amount": 100,
    }


def test_report_decorator_with_dataframe(tmp_path):
    filename = tmp_path / "report.json"

    @report(str(filename))
    def create_report():
        return pd.DataFrame(
            {
                "Категория": ["Супермаркеты"],
                "Сумма операции": [-100.0],
            }
        )

    result = create_report()

    assert isinstance(result, pd.DataFrame)

    with open(filename, encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == [
        {
            "Категория": "Супермаркеты",
            "Сумма операции": -100.0,
        }
    ]


def test_report_decorator_default_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    @report
    def create_report():
        return {"result": 123}

    create_report()

    assert (tmp_path / "report.json").exists()


def test_report_decorator_with_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    @report("custom_report.json")
    def create_report():
        return {"result": 123}

    create_report()

    assert (tmp_path / "custom_report.json").exists()


def test_spending_by_category_includes_start_date():
    transactions = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                [
                    "2021-10-01 00:00:00",
                    "2021-09-30 23:59:59",
                ]
            ),
            "Сумма операции": [-100.0, -200.0],
            "Категория": [
                "Супермаркеты",
                "Супермаркеты",
            ],
        }
    )

    result = spending_by_category(
        transactions,
        "Супермаркеты",
        "2021-12-31",
    )

    assert len(result) == 1
    assert result.iloc[0]["Сумма операции"] == -100.0