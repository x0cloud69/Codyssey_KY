# python -m budget_app 하면 실행되는 진입점

import sys
from .cli import main

#def main() -> int:
#    print("budget_app -- 사용법 python -m budget_app <command>")
#    print("commands : add, list, search, budget, category, update, delete, import, export")
#    return 0

if __name__ == "__main__":
    sys.exit(main())
