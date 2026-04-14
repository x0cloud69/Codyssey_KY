import argparse
import json
from pathlib import Path
from typing import Any


def _is_scalar(x: Any) -> bool:
    return x is None or isinstance(x, (str, int, float, bool))


def _is_inline_list(a: Any, max_len: int) -> bool:
    return isinstance(a, list) and len(a) <= max_len and all(_is_scalar(x) for x in a)


def dumps_inline_lists(obj: Any, *, indent: int = 2, level: int = 0, max_inline_len: int = 80) -> str:
    sp = " " * (indent * level)

    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items: list[str] = []
        for k, v in obj.items():
            key = json.dumps(k, ensure_ascii=False)
            items.append((" " * (indent * (level + 1))) + key + ": " + dumps_inline_lists(v, indent=indent, level=level + 1, max_inline_len=max_inline_len))
        return "{\n" + ",\n".join(items) + "\n" + sp + "}"

    if isinstance(obj, list):
        if not obj:
            return "[]"
        if _is_inline_list(obj, max_inline_len):
            return "[" + ",".join(json.dumps(x, ensure_ascii=False) for x in obj) + "]"
        parts = [(" " * (indent * (level + 1))) + dumps_inline_lists(it, indent=indent, level=level + 1, max_inline_len=max_inline_len) for it in obj]
        return "[\n" + ",\n".join(parts) + "\n" + sp + "]"

    return json.dumps(obj, ensure_ascii=False)


def main() -> None:
    ap = argparse.ArgumentParser(description="Format JSON with inline scalar lists.")
    ap.add_argument("path", type=Path)
    ap.add_argument("--indent", type=int, default=2)
    ap.add_argument("--max-inline-len", type=int, default=80)
    args = ap.parse_args()

    data = json.loads(args.path.read_text(encoding="utf-8"))
    out = dumps_inline_lists(data, indent=args.indent, max_inline_len=args.max_inline_len) + "\n"
    args.path.write_text(out, encoding="utf-8")


if __name__ == "__main__":
    main()

