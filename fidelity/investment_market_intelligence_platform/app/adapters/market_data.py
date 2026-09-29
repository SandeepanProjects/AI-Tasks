from typing import Protocol
from datetime import datetime
from pydantic import BaseModel

class MarketObservation(BaseModel):
    symbol: str
    price: float | None
    currency: str
    observed_at: datetime
    provider: str
    is_delayed: bool
    methodology: str

class MarketDataProvider(Protocol):
    async def get_observations(self, symbols: list[str], lookback_days: int) -> list[MarketObservation]: ...

class UnconfiguredMarketDataProvider:
    async def get_observations(self, symbols: list[str], lookback_days: int) -> list[MarketObservation]:
        # Fail closed rather than fabricating market prices.
        raise RuntimeError("No licensed market-data provider configured")
