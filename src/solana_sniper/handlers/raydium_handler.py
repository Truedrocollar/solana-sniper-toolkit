"""Raydium AMM v4 initialize2 program-log parser."""
from __future__ import annotations

import base58
import structlog

from solana_sniper.core.pool_event import DexKind, PoolEvent

log = structlog.get_logger(__name__)

RAYDIUM_AMM_V4 = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
INITIALIZE2_DISC = "afaf6d1f0d989bed"  # 8-byte sighash of initialize2


class RaydiumHandler:
    """Parses Raydium initialize2 logs into PoolEvent."""

    dex = DexKind.RAYDIUM_AMM

    def matches(self, log_messages: list[str]) -> bool:
        return any(f"Program log: Instruction: Initialize2" in m for m in log_messages)

    def parse(self, log_messages: list[str], slot: int, signature: str, ts_ms: int) -> PoolEvent | None:
        # Raydium emits base/quote vaults as account keys after "init_pc_amount"
        try:
            base_mint = self._extract(log_messages, "base mint")
            quote_mint = self._extract(log_messages, "quote mint")
            pool = self._extract(log_messages, "amm id")
        except KeyError as exc:
            log.debug("raydium.parse.miss", missing=str(exc))
            return None

        return PoolEvent(
            dex=self.dex,
            pool_address=pool,
            base_mint=base_mint,
            quote_mint=quote_mint,
            base_vault="",
            quote_vault="",
            open_price_sol=0.0,
            liquidity_sol=0.0,
            slot=slot,
            signature=signature,
            observed_at_ms=ts_ms,
        )

    @staticmethod
    def _extract(logs: list[str], needle: str) -> str:
        for m in logs:
            if needle in m:
                raw = m.split(needle, 1)[1].strip(" :").split()[0]
                return base58.b58encode(base58.b58decode(raw)).decode()
        raise KeyError(needle)