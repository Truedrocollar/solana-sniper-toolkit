"""Pump.fun create-event parser from program logs."""
from __future__ import annotations

import structlog

from solana_sniper.core.pool_event import DexKind, PoolEvent

log = structlog.get_logger(__name__)

PUMPFUN_PROGRAM = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"


class PumpFunHandler:
    dex = DexKind.PUMPFUN

    def matches(self, log_messages: list[str]) -> bool:
        return any("Program log: Instruction: Create" in m for m in log_messages)

    def parse(self, log_messages: list[str], slot: int, signature: str, ts_ms: int) -> PoolEvent | None:
        mint = next((m.split("mint:")[-1].strip() for m in log_messages if "mint:" in m), None)
        if not mint:
            log.debug("pumpfun.parse.miss", sig=signature)
            return None
        return PoolEvent(
            dex=self.dex,
            pool_address=mint,
            base_mint=mint,
            quote_mint="So11111111111111111111111111111111111111112",
            base_vault="",
            quote_vault="",
            open_price_sol=0.0,
            liquidity_sol=0.0,
            slot=slot,
            signature=signature,
            observed_at_ms=ts_ms,
        )