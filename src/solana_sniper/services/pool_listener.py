"""WebSocket log listener. Feeds matched PoolEvents into the dispatcher."""
from __future__ import annotations

import asyncio
import json
import time

import structlog
import websockets

from solana_sniper.config.settings import SniperSettings
from solana_sniper.core.dispatcher import SnipeDispatcher
from solana_sniper.handlers import PumpFunHandler, RaydiumHandler

log = structlog.get_logger(__name__)

HANDLERS = (RaydiumHandler(), PumpFunHandler())
RECONNECT_BACKOFF_S = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0)


class PoolListener:
    def __init__(self, ws_url: str, settings: SniperSettings, dispatcher: SnipeDispatcher) -> None:
        self._ws_url = ws_url
        self._settings = settings
        self._dispatcher = dispatcher

    async def run(self) -> None:
        backoff = 0
        while True:
            try:
                await self._connect_once()
                backoff = 0
            except (websockets.ConnectionClosed, OSError) as exc:
                wait = RECONNECT_BACKOFF_S[min(backoff, len(RECONNECT_BACKOFF_S) - 1)]
                log.warning("listener.reconnect", err=str(exc), wait_s=wait)
                await asyncio.sleep(wait)
                backoff += 1

    async def _connect_once(self) -> None:
        async with websockets.connect(self._ws_url, ping_interval=20, max_queue=4096) as ws:
            await ws.send(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "logsSubscribe",
                        "params": [
                            {"mentions": [
                                "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
                                "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P",
                            ]},
                            {"commitment": "processed"},
                        ],
                    }
                )
            )
            log.info("listener.subscribed", url=self._ws_url)

            async for raw in ws:
                await self._handle_raw(raw)

    async def _handle_raw(self, raw: str | bytes) -> None:
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            return
        params = msg.get("params", {})
        result = params.get("result", {})
        value = result.get("value", {})
        logs = value.get("logs") or []
        sig = value.get("signature")
        slot = value.get("slot")
        if not sig or not logs:
            return

        ts_ms = int(time.time() * 1000)
        for handler in HANDLERS:
            if handler.matches(logs):
                event = handler.parse(logs, slot=slot, signature=sig, ts_ms=ts_ms)
                if event:
                    asyncio.create_task(self._dispatcher.on_pool_event(event))