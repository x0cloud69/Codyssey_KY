from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import date
from .config import TRANSACTION_TYPES

@dataclass
class Transaction:
    id: str
    type: str
    date: str
    amount: int
    category:str
    memo: str = ""
    tags: list[str]=field(default_factory=list)
    
    def __post_init__(self) -> None:
        if self.type not in TRANSACTION_TYPES:
            raise ValueError(f"type은 income/expense 만 됩니다: {self.type!r}")
        if not isinstance(self.amount, int) or self.amount <= 0:
            raise ValueError(f"amount는 양의 정수여야 합니다: {self.amount!r}")
        try:
            date.fromisoformat(self.date)
        except ValueError:
            raise ValueError(f"날짜 형식이 올바르지 않습니다 (YYYY-MM-DD) {self.date!r}")
        if not self.category.strip():
            raise ValueError("category는 비어 있을 수 없습니다")  
        
    def to_dict(self) -> dict:
        return asdict(self)    #dataclass 객체를 자동으로 dict 로 바꿔주는 파이썬 도구
    
    @classmethod
    def from_dict(cls, d: dict) -> "Transaction":
        return cls(
            id=d["id"],
            type=d["type"],
            date=d["date"],
            amount=int(d["amount"]),
            category=d["category"],
            memo=d.get("memo",""),
            tags=list(d.get("tags",[])),            
        )
                                 

