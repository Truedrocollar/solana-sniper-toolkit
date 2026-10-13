"""Receives PoolEvents, runs rug heuristics, and fires Jito bundles concurrently."""
from __future__ import annotations

import asyncio

import structlog
from solana.rpc.async_api import AsyncClient

from solana_sniper.config.settings import SniperSettings
from solana_sniper.core.pool_event import PoolEvent
from solana_sniper.models.snipe_attempt import SnipeAttempt, SnipeOutcome
from solana_sniper.services.jito_bundler import JitoBundler
from solana_sniper.services.rug_checker import RugChecker
from solana_sniper.services.wallet_loader import WalletLoader
from solana_sniper.dex import REGISTRY

log = structlog.get_logger(__name__)


class SnipeDispatcher:
    def __init__(self, rpc: AsyncClient, settings: SniperSettings) -> None:
        self._rpc = rpc
        self._settings = settings
        self._wallet = WalletLoader(settings).load()
        self._checker = RugChecker(settings)
        self._bundler = JitoBundler(settings, self._wallet)
        self._sem = asyncio.Semaphore(settings.max_concurrent_snipes)

    async def on_pool_event(self, event: PoolEvent) -> None:
        async with self._sem:
            await self._handle(event)

    async def _handle(self, event: PoolEvent) -> None:
        report = await self._checker.check(event.base_mint, event=event)
        attempt = SnipeAttempt(event=event, report=report)

        if not report.passed:
            attempt.outcome = SnipeOutcome.SKIPPED_RUG
            log.warning("snipe.skip", mint=event.base_mint, reasons=report.failures)
            return

        adapter = REGISTRY[event.dex]()
        try:
            tx = await adapter.build_buy_tx(
                event=event,
                payer=self._wallet.pubkey(),
                amount_sol=self._settings.snipe_amount_sol,
                slippage_bps=self._settings.slippage_bps,
                priority_fee_microlamports=self._settings.priority_fee_microlamports,
            )
        except Exception as exc:  # adapter-specific build failure
            attempt.outcome = SnipeOutcome.BUILD_FAILED
            log.error("snipe.build_failed", dex=event.dex, err=str(exc))
            return

        sig = await self._bundler.send_bundle([tx])
        attempt.outcome = SnipeOutcome.SUBMITTED if sig else SnipeOutcome.SEND_FAILED
        attempt.signature = sig
        log.info("snipe.result", mint=event.base_mint, outcome=attempt.outcome, sig=sig)