from src.utils import load_transactions, prepare_transactions
from src.views import main_page


def main() -> None:
    """Запускает приложение."""
    transactions = load_transactions()
    transactions = prepare_transactions(transactions)

    result = main_page(
        "2021-12-31 23:59:59",
        transactions,
    )

    print(result)


if __name__ == "__main__":
    main()