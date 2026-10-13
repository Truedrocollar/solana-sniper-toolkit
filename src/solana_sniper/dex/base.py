"""Abstract DEX adapter. Every concrete DEX implements build_buy_tx/build_sell_tx."""
from __future__ import annotations

from abc import ABC, abstractmethod

from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction

from solana_sniper.core.pool_event import DexKind, PoolEvent


class BaseDex(ABC):
    dex: DexKind

    @abstractmethod
    async def build_buy_tx(
        self,
        *,
        event: PoolEvent,
        payer: Pubkey,
        amount_sol: float,
        slippage_bps: int,
        priority_fee_microlamports: int,
    ) -> VersionedTransaction: ...

    @abstractmethod
    async def build_sell_tx(
        self,
        *,
        event: PoolEvent,
        payer: Pubkey,
        amount_tokens: int,
        slippage_bps: int,
        priority_fee_microlamports: int,
    ) -> VersionedTransaction: ...