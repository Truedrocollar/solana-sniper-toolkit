"""Runtime bootstrap: wire config, logger, RPC client, and dispatcher."""
from __future__ import annotations

import asyncio
import signal
from contextlib import suppress

import structlog
from solana.rpc.async_api import AsyncClient

from solana_sniper.config.settings import SniperSettings
from solana_sniper.core.dispatcher import SnipeDispatcher
from solana_sniper.services.pool_listener import PoolListener
from solana_sniper.utils.logging import configure_logging

log = structlog.get_logger(__name__)


async def _run(settings: SniperSettings) -> None:
    configure_logging(settings.log_level, settings.log_json)
    log.info("bootstrap.start", rpc=settings.solana_rpc_url, ws=settings.solana_ws_url)

    async with AsyncClient(settings.solana_rpc_url, commitment="processed") as rpc:
        dispatcher = SnipeDispatcher(rpc, settings)
        listener = PoolListener(settings.solana_ws_url, settings, dispatcher)

        stop = asyncio.Event()

        def _shutdown(*_: object) -> None:
            log.warning("bootstrap.signal", stopping=True)
            stop.set()

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            with suppress(NotImplementedError):
                loop.add_signal_handler(sig, _shutdown)

        listener_task = asyncio.create_task(listener.run(), name="pool-listener")
        stop_task = asyncio.create_task(stop.wait(), name="stop-wait")

        done, pending = await asyncio.wait(
            {listener_task, stop_task}, return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
        for task in done:
            exc = task.exception()
            if exc:
                log.error("bootstrap.task_failed", task=task.get_name(), err=str(exc))
                raise exc

    log.info("bootstrap.stop")


def main() -> None:
    settings = SniperSettings()
    asyncio.run(_run(settings))