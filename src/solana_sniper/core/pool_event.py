"""Normalized pool event emitted by every DEX adapter."""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class DexKind(StrEnum):
    RAYDIUM_AMM = "raydium_amm"
    RAYDIUM_CPMM = "raydium_cpmm"
    PUMPFUN = "pumpfun"
    ORCA_WHIRLPOOL = "orca_whirlpool"
    METEORA_DLMM = "meteora_dlmm"


class PoolEvent(BaseModel):
    """Canonical event shape. Adapters MUST produce this and only this."""

    dex: DexKind
    pool_address: str
    base_mint: str
    quote_mint: str
    base_vault: str
    quote_vault: str
    open_price_sol: float = Field(ge=0.0)
    liquidity_sol: float = Field(ge=0.0)
    slot: int
    signature: str
    observed_at_ms: int = Field(description="Unix ms when the listener observed the pool.")