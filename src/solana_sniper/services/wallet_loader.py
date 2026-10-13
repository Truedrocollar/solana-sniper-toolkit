"""Loads the sniper keypair from env (base58) or a JSON keypair file."""
from __future__ import annotations

import json
import pathlib

import base58
import structlog
from solders.keypair import Keypair

from solana_sniper.config.settings import SniperSettings

log = structlog.get_logger(__name__)


class WalletLoader:
    def __init__(self, settings: SniperSettings) -> None:
        self._s = settings

    def load(self) -> Keypair:
        if self._s.sniper_keypair_base58:
            raw = base58.b58decode(self._s.sniper_keypair_base58)
            return Keypair.from_bytes(raw)

        path = pathlib.Path(self._s.sniper_keypair_path or "")
        if not path.exists():
            raise FileNotFoundError(f"sniper keypair not found at {path}")
        data = json.loads(path.read_text())
        if isinstance(data, dict) and "secretKey" in data:
            raw = bytes(data["secretKey"])
        else:
            raw = bytes(data)
        kp = Keypair.from_bytes(raw)
        log.info("wallet.loaded", pubkey=str(kp.pubkey()))
        return kp