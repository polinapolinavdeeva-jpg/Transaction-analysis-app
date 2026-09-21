import json
from pathlib import Path
import pandas as pd
import os
from dotenv import load_dotenv



BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "operations.xlsx"
SETTINGS_PATH = BASE_DIR / "user_settings.json"


def load_transactions(path: Path = DATA_PATH) -> pd.DataFrame:
    """Загружает транзакции из Excel."""
    return pd.read_excel(path)


def prepare_transactions(transactions: pd.DataFrame) -> pd.DataFrame:
    """Подготавливает данные о транзакциях."""
    transactions = transactions.copy()

    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"],
        format="%d.%m.%Y %H:%M:%S",
    )

    return transactions


def load_user_settings(path: Path = SETTINGS_PATH) -> dict:
    """Загружает пользовательские настройки."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


load_dotenv()

def get_stock_api_key() -> str:
    return os.getenv("STOCK_API_KEY", "")