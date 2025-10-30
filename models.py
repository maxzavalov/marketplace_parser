from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TrackedProduct:
    id: int
    user_id: int
    name: str
    search_query: str
    marketplace: str
    target_price: float
    current_price: float
    product_url: Optional[str] = None
    is_active: bool = True
    created_at: str = None
    last_checked: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.last_checked is None:
            self.last_checked = datetime.now().isoformat()


@dataclass
class PriceHistory:
    id: int
    product_id: int
    price: float
    checked_at: str = None

    def __post_init__(self):
        if self.checked_at is None:
            self.checked_at = datetime.now().isoformat()