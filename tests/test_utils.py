import json

from src.utils import load_user_settings


def test_load_user_settings(tmp_path):
    settings_file = tmp_path / "user_settings.json"

    settings = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"],
    }

    settings_file.write_text(
        json.dumps(settings),
        encoding="utf-8",
    )

    result = load_user_settings(settings_file)

    assert result == settings