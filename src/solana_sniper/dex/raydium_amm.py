"""Raydium AMM v4 buy/sell tx builder (swapBaseIn / swapBaseOut)."""
from __future__ import annotations

import structlog
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction

from solana_sniper.core.pool_event import DexKind, PoolEvent
from solana_sniper.dex.base import BaseDex

log = structlog.get_logger(__name__)

RAYDIUM_AMM_V4 = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")


class RaydiumAmmAdapter(BaseDex):
    dex = DexKind.RAYDIUM_AMM

    async def build_buy_tx(
        self,
        *,
        event: PoolEvent,
        payer: Pubkey,
        amount_sol: float,
        slippage_bps: int,
        priority_fee_microlamports: int,
    ) -> VersionedTransaction:
        # Placeholder wiring — real build requires the pool's market account
        # (open_orders, bids, asks, event queue) which the initialize2 log
        # exposes on the account-key list. Extend in a follow-up.
        log.info("raydium_amm.build_buy", pool=event.pool_address, sol=amount_sol)
        raise NotImplementedError("raydium_amm build_buy_tx pending account-map wiring")

    async def build_sell_tx(
        self,
        *,
        event: PoolEvent,
        payer: Pubkey,
        amount_tokens: int,
        slippage_bps: int,
        priority_fee_microlamports: int,
    ) -> VersionedTransaction:
        raise NotImplementedError("raydium_amm build_sell_tx pending account-map wiring")