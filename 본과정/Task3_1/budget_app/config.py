#경로 / 상수 한곳에 모으기

from pathlib import Path
DATA_DIR = Path("./data")
TRANSACTIONS_FILE = DATA_DIR / "transactions.jsonl"
CATEGORIES_FILE = DATA_DIR/ "categories.jsonl"
BUDGETS_FILE = DATA_DIR / "budgets.jsonl"
TRANSACTION_TYPES = ("income","expense")
