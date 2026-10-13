"""Pydantic settings loaded from env / .env. All sniping params live here."""
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SniperSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    solana_rpc_url: str = Field(..., alias="SOLANA_RPC_URL")
    solana_ws_url: str = Field(..., alias="SOLANA_WS_URL")
    jito_block_engine_url: str = Field("https://mainnet.block-engine.jito.wtf", alias="JITO_BLOCK_ENGINE_URL")
    jito_tip_lamports: int = Field(1_000_000, alias="JITO_TIP_LAMPORTS")
    jito_tip_account: str = Field(
        "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5", alias="JITO_TIP_ACCOUNT"
    )

    sniper_keypair_path: str | None = Field("./.wallets/sniper.json", alias="SNIPER_KEYPAIR_PATH")
    sniper_keypair_base58: str | None = Field(None, alias="SNIPER_KEYPAIR_BASE58")

    snipe_amount_sol: float = Field(0.05, alias="SNIPE_AMOUNT_SOL")
    slippage_bps: int = Field(1500, alias="SLIPPAGE_BPS")
    max_concurrent_snipes: int = Field(3, alias="MAX_CONCURRENT_SNIPES")
    priority_fee_microlamports: int = Field(100_000, alias="PRIORITY_FEE_MICROLAMPORTS")

    rug_min_liquidity_sol: float = Field(5.0, alias="RUG_MIN_LIQUIDITY_SOL")
    rug_max_top10_pct: float = Field(35.0, alias="RUG_MAX_TOP10_PCT")
    rug_max_snipe_pct: float = Field(25.0, alias="RUG_MAX_SNIPE_PCT")
    require_mint_revoked: bool = Field(True, alias="REQUIRE_MINT_REVOKED")
    require_freeze_revoked: bool = Field(True, alias="REQUIRE_FREEZE_REVOKED")

    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_json: bool = Field(False, alias="LOG_JSON")