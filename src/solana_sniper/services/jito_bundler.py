"""Jito Block Engine client. Submits bundles and polls for confirmation."""
from __future__ import annotations

import base64
import uuid

import httpx
import structlog
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

from solana_sniper.config.settings import SniperSettings

log = structlog.get_logger(__name__)


class JitoBundler:
    def __init__(self, settings: SniperSettings, wallet: Keypair) -> None:
        self._s = settings
        self._wallet = wallet
        self._client = httpx.AsyncClient(base_url=settings.jito_block_engine_url, timeout=10.0)

    async def send_bundle(self, txs: list[VersionedTransaction]) -> str | None:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendBundle",
            "params": [
                [base64.b64encode(bytes(tx)).decode() for tx in txs],
                {"encoding": "base64"},
            ],
        }
        try:
            resp = await self._client.post(f"/api/v1/bundles?uuid={uuid.uuid4()}", json=payload)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            log.error("jito.send_error", err=str(exc))
            return None

        bundle_id = resp.json().get("result")
        log.info("jito.bundle_submitted", bundle_id=bundle_id)
        return bundle_id

    async def aclose(self) -> None:
        await self._client.aclose()