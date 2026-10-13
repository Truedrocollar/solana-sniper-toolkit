"""DEX adapter registry. `REGISTRY[event.dex]()` returns a fresh adapter."""
from __future__ import annotations

from solana_sniper.core.pool_event import DexKind
from solana_sniper.dex.base import BaseDex
from solana_sniper.dex.raydium_cpmm import RaydiumCpmmAdapter
from solana_sniper.dex.raydium_amm import RaydiumAmmAdapter
from solana_sniper.dex.pumpfun import PumpFunAdapter

REGISTRY: dict[DexKind, type[BaseDex]] = {
    DexKind.RAYDIUM_AMM: RaydiumAmmAdapter,
    DexKind.RAYDIUM_CPMM: RaydiumCpmmAdapter,
    DexKind.PUMPFUN: PumpFunAdapter,
}

__all__ = ["REGISTRY", "BaseDex"]