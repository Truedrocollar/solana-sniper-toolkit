"""Raydium CPMM (constant-product) adapter — simplest snipe target."""
from __future__ import annotations

import structlog
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction

from solana_sniper.core.pool_event import DexKind, PoolEvent
from solana_sniper.dex.base import BaseDex

log = structlog.get_logger(__name__)

RAYDIUM_CPMM = Pubkey.from_string("CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C")


class RaydiumCpmmAdapter(BaseDex):
    dex = DexKind.RAYDIUM_CPMM

    async def build_buy_tx(
        self,
        *,