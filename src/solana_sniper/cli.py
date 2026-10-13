"""Click CLI entrypoint. `sniper listen`, `sniper watch <mint>`, `sniper rugcheck <mint>`."""
from __future__ import annotations

import asyncio
import json

import click

from solana_sniper.bootstrap import main as bootstrap_main
from solana_sniper.config.settings import SniperSettings
from solana_sniper.services.rug_checker import RugChecker
from solana_sniper.utils.logging import configure_logging


@click.group()
def main() -> None:
    """solana-sniper-toolkit — snipe new Solana pools with rug heuristics."""


@main.command("listen")
def listen_cmd() -> None:
    """Start the pool listener + snipe dispatcher (long-running)."""
    bootstrap_main()


@main.command("rugcheck")
@click.argument("mint")
def rugcheck_cmd(mint: str) -> None:
    """One-shot rug check on a mint address."""
    settings = SniperSettings()
    configure_logging(settings.log_level, settings.log_json)

    async def _go() -> None:
        checker = RugChecker(settings)
        report = await checker.check(mint)
        click.echo(json.dumps(report.model_dump(), indent=2))

    asyncio.run(_go())


if __name__ == "__main__":
    main()