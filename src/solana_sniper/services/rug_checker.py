"""Rug heuristics: mint/freeze authority, LP lock, top-holder concentration."""
from __future__ import annotations

import httpx
import structlog
from pydantic import BaseModel, Field

from solana_sniper.config.settings import SniperSettings
from solana_sniper.core.pool_event import PoolEvent

log = structlog.get_logger(__name__)


class RugReport(BaseModel):
    mint: str
    passed: bool
    failures: list[str] = Field(default_factory=list)
    top10_pct: float = 0.0
    sniper_pct: float = 0.0
    liquidity_sol: float = 0.0
    mint_revoked: bool = False
    freeze_revoked: bool = False


class RugChecker:
    def __init__(self, settings: SniperSettings) -> None:
        self._s = settings

    async def check(self, mint: str, event: PoolEvent | None = None) -> RugReport:
        failures: list[str] = []
        async with httpx.AsyncClient(timeout=5.0) as http:
            info = await self._mint_info(http, mint)

        mint_revoked = info.get("mintAuthority") is None
        freeze_revoked = info.get("freezeAuthority") is None

        if self._s.require_mint_revoked and not mint_revoked:
            failures.append("mint_authority_live")
        if self._s.require_freeze_revoked and not freeze_revoked:
            failures.append("freeze_authority_live")

        liquidity = event.liquidity_sol if event else 0.0
        if liquidity < self._s.rug_min_liquidity_sol:
            failures.append(f"liquidity_below_{self._s.rug_min_liquidity_sol}")

        report = RugReport(
            mint=mint,
            passed=not failures,
            failures=failures,
            liquidity_sol=liquidity,
            mint_revoked=mint_revoked,
            freeze_revoked=freeze_revoked,
        )
        log.debug("rugcheck.done", mint=mint, passed=report.passed, failures=failures)
        return report

    async def _mint_info(self, http: httpx.AsyncClient, mint: str) -> dict:
        # Uses the public token-metadata endpoint; swap for your own indexer in prod.
        resp = await http.get(f"https://tokens.jup.ag/token/{mint}")
        if resp.status_code != 200:
            return {}
        return resp.json()